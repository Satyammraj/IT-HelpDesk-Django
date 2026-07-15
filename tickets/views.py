from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, TicketForm
from .models import Ticket, TicketHistory
from django.core.paginator import Paginator

# =====================================
# Dashboard
# =====================================


@login_required
def dashboard(request):

    if request.user.is_staff:

        tickets = Ticket.objects.all()

        context = {
            "admin": True,
            "total_users": User.objects.count(),
            "total_tickets": tickets.count(),
            "active_tickets": tickets.exclude(status="Closed").count(),
            "closed_tickets": tickets.filter(status="Closed").count(),
            "high_priority": tickets.filter(priority="High").count(),
            "today_tickets": tickets.filter(created__date=date.today()).count(),
            "recent_users": User.objects.order_by("-date_joined")[:5],
            "recent_tickets": tickets.order_by("-created")[:5],
        }

    else:

        tickets = Ticket.objects.filter(created_by=request.user)

        context = {
            "admin": False,
            "total_tickets": tickets.count(),
            "active_tickets": tickets.exclude(status="Closed").count(),
            "closed_tickets": tickets.filter(status="Closed").count(),
            "high_priority": tickets.filter(priority="High").count(),
            "recent_tickets": tickets.order_by("-created")[:5],
        }

    return render(
        request,
        "tickets/dashboard.html",
        context,
    )


# =====================================
# Ticket List
# =====================================


@login_required
def ticket_list(request):

    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    category = request.GET.get("category", "")

    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(created_by=request.user)

    if search:

        tickets = tickets.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(category__icontains=search)
        )

    if status:
        tickets = tickets.filter(status=status)

    if priority:
        tickets = tickets.filter(priority=priority)

    if category:
        tickets = tickets.filter(category=category)

    tickets = tickets.order_by("-created")

    paginator = Paginator(tickets, 10)

    page_number = request.GET.get("page")

    tickets = paginator.get_page(page_number)

    return render(
        request,
        "tickets/ticket_list.html",
        {
            "tickets": tickets,
            "search": search,
            "status": status,
            "priority": priority,
            "category": category,
        },
    )


# =====================================
# Create Ticket
# =====================================


@login_required
def create_ticket(request):

    if request.method == "POST":

        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():

            ticket = form.save(commit=False)

            ticket.created_by = request.user
            ticket.status = "Open"

            ticket.save()

            # Create timeline entry
            TicketHistory.objects.create(
                ticket=ticket,
                user=request.user,
                action="Ticket Created",
            )

            # Notify all admins
            # admin_emails = list(
            #     User.objects.filter(is_staff=True)
            #     .exclude(email="")
            #     .values_list("email", flat=True)
            # )

            # if admin_emails:

            #     send_mail(
            #         subject=f"New Ticket: {ticket.title}",
            #         message=(
            #             f"A new support ticket has been created.\n\n"
            #             f"Title: {ticket.title}\n"
            #             f"Category: {ticket.category}\n"
            #             f"Priority: {ticket.priority}\n"
            #             f"Created By: {request.user.username}\n\n"
            #             f"Please log in to the IT Help Desk to review it."
            #         ),
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=admin_emails,
            #         fail_silently=True,
            #     )

            messages.success(request, f'Ticket "{ticket.title}" created successfully.')

            return redirect("dashboard")

        else:

            messages.error(request, "Please correct the errors below.")

    else:

        form = TicketForm()

    return render(request, "tickets/create_ticket.html", {"form": form})


# =====================================
# Edit Ticket
# =====================================


@login_required
def edit_ticket(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:

        messages.error(request, "You don't have permission to edit this ticket.")

        return redirect("ticket_list")

    if request.method == "POST":

        form = TicketForm(request.POST, request.FILES, instance=ticket)

        if form.is_valid():

            form.save()

            TicketHistory.objects.create(
                ticket=ticket,
                user=request.user,
                action="Ticket Updated",
                details="Ticket details were modified.",
            )

            messages.success(request, f'Ticket "{ticket.title}" updated successfully.')

            return redirect("ticket_list")

        else:

            messages.error(request, "Please correct the errors below.")

    else:

        form = TicketForm(instance=ticket)

    return render(
        request,
        "tickets/edit_ticket.html",
        {
            "form": form,
            "ticket": ticket,
        },
    )

    # =====================================


# Ticket Detail
# =====================================


@login_required
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:

        messages.error(request, "You don't have permission to view this ticket.")

        return redirect("ticket_list")

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.ticket = ticket
            comment.user = request.user

            comment.save()

            # Timeline
            TicketHistory.objects.create(
                ticket=ticket,
                user=request.user,
                action="Comment Added",
                details=comment.message,
            )

            # Email user if admin replies
            if (
                request.user.is_staff
                and ticket.created_by != request.user
                and ticket.created_by.email
            ):

                send_mail(
                    subject=f"New Reply: {ticket.title}",
                    message=(
                        f"Hello {ticket.created_by.username},\n\n"
                        f"An administrator replied to your ticket.\n\n"
                        f"Reply:\n\n"
                        f"{comment.message}\n\n"
                        f"Please log in to continue the conversation."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.created_by.email],
                    fail_silently=True,
                )

            messages.success(request, "Reply added successfully.")

            return redirect("ticket_detail", ticket.id)

        else:

            messages.error(request, "Please correct the errors below.")

    else:

        form = CommentForm()

    return render(
        request,
        "tickets/ticket_detail.html",
        {
            "ticket": ticket,
            "form": form,
            "history": ticket.history.all(),
        },
    )


# =====================================
# Close Ticket
# =====================================


@login_required
def close_ticket(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:

        messages.error(request, "You don't have permission to close this ticket.")

        return redirect("ticket_list")

    if ticket.status == "Closed":

        messages.info(request, f'Ticket "{ticket.title}" is already closed.')

        return redirect("ticket_detail", ticket.id)

    old_status = ticket.status

    ticket.status = "Closed"
    ticket.resolved_on = timezone.now()

    ticket.save()

    TicketHistory.objects.create(
        ticket=ticket,
        user=request.user,
        action="Status Updated",
        details=f"{old_status} → Closed",
    )

    if ticket.created_by.email and ticket.created_by.profile.email_notifications:
        send_mail(
            subject=f"Ticket Closed: {ticket.title}",
            message=(
                f"Hello {ticket.created_by.username},\n\n"
                f"Your ticket has been marked as Closed.\n\n"
                f"Title: {ticket.title}\n\n"
                f"Thank you for using the IT Help Desk."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.created_by.email],
            fail_silently=True,
        )

    messages.success(request, f'Ticket "{ticket.title}" closed successfully.')

    return redirect("ticket_list")


# =====================================
# Admin Status Update
# =====================================


@login_required
def update_status(request, ticket_id):

    if not request.user.is_staff:

        messages.error(request, "Only administrators can update ticket status.")

        return redirect("ticket_detail", ticket_id)

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":

        old_status = ticket.status
        new_status = request.POST.get("status")

        ticket.status = new_status

        if new_status == "Closed":
            ticket.resolved_on = timezone.now()
        else:
            ticket.resolved_on = None

        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action="Status Updated",
            details=f"{old_status} → {new_status}",
        )

        if (ticket.created_by.email and ticket.created_by.profile.email_notifications):

            send_mail(
                subject=f"Ticket Status Updated: {ticket.title}",
                message=(
                    f"Hello {ticket.created_by.username},\n\n"
                    f"The status of your ticket has been updated.\n\n"
                    f"Title: {ticket.title}\n"
                    f"Previous Status: {old_status}\n"
                    f"New Status: {new_status}\n\n"
                    f"Please log in to the IT Help Desk for more details."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ticket.created_by.email],
                fail_silently=True,
            )

        messages.success(request, f'Ticket "{ticket.title}" status updated.')

    return redirect("ticket_detail", ticket.id)


# =====================================
# Delete Ticket
# =====================================


@login_required
def delete_ticket(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:

        messages.error(request, "You don't have permission to delete this ticket.")

        return redirect("ticket_list")

    ticket_title = ticket.title

    # No TicketHistory entry here because deleting the ticket
    # also deletes its history (CASCADE).

    ticket.delete()

    messages.success(request, f'Ticket "{ticket_title}" deleted successfully.')

    return redirect("ticket_list")

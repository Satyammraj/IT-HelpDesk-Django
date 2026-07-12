from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Ticket
from .forms import TicketForm, CommentForm


# =====================================
# Dashboard
# =====================================

@login_required
def dashboard(request):

    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(created_by=request.user)

    context = {
        "total_tickets": tickets.count(),
        "active_tickets": tickets.exclude(status="Closed").count(),
        "closed_tickets": tickets.filter(status="Closed").count(),
        "high_priority": tickets.filter(priority="High").count(),
        "recent_tickets": tickets.order_by("-created")[:5],
    }

    return render(
        request,
        "tickets/dashboard.html",
        context
    )


# =====================================
# Ticket List
# =====================================

@login_required
def ticket_list(request):

    search = request.GET.get("search", "")

    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(created_by=request.user)

    if search:

        tickets = tickets.filter(

            Q(title__icontains=search) |
            Q(category__icontains=search) |
            Q(priority__icontains=search) |
            Q(status__icontains=search)

        )

    tickets = tickets.order_by("-created")

    return render(
        request,
        "tickets/ticket_list.html",
        {
            "tickets": tickets,
            "search": search
        }
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

            return redirect("ticket_list")

    else:

        form = TicketForm()

    return render(
        request,
        "tickets/create_ticket.html",
        {
            "form": form
        }
    )


# =====================================
# Edit Ticket
# =====================================

@login_required
def edit_ticket(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:
        return redirect("ticket_list")

    if request.method == "POST":

        form = TicketForm(
            request.POST,
            request.FILES,
            instance=ticket
        )

        if form.is_valid():

            form.save()

            return redirect("ticket_detail", ticket.id)

    else:

        form = TicketForm(instance=ticket)

    return render(
        request,
        "tickets/edit_ticket.html",
        {
            "form": form,
            "ticket": ticket
        }
    )


# =====================================
# Ticket Detail
# =====================================

@login_required
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:
        return redirect("ticket_list")

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.ticket = ticket

            comment.user = request.user

            comment.save()

            return redirect("ticket_detail", ticket.id)

    else:

        form = CommentForm()

    return render(
        request,
        "tickets/ticket_detail.html",
        {
            "ticket": ticket,
            "form": form,
        }
    )


# =====================================
# User Close Ticket
# =====================================

@login_required
def close_ticket(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.created_by != request.user:
        return redirect("ticket_list")

    ticket.status = "Closed"

    ticket.resolved_on = timezone.now()

    ticket.save()

    return redirect("ticket_detail", ticket.id)


# =====================================
# Admin Status Update
# =====================================

@login_required
def update_status(request, ticket_id):

    if not request.user.is_staff:
        return redirect("ticket_detail", ticket_id)

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":

        ticket.status = request.POST.get("status")

        if ticket.status == "Closed":
            ticket.resolved_on = timezone.now()
        else:
            ticket.resolved_on = None

        ticket.save()

    return redirect("ticket_detail", ticket.id)


# =====================================
# Delete Ticket
# =====================================

@login_required
def delete_ticket(request, ticket_id):

    if not request.user.is_staff:
        return redirect("ticket_list")

    ticket = get_object_or_404(Ticket, id=ticket_id)

    ticket.delete()

    return redirect("ticket_list")
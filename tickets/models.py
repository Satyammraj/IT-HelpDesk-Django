from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):

    CATEGORY_CHOICES = [
        ("Hardware", "Hardware"),
        ("Software", "Software"),
        ("Network", "Network"),
        ("Account", "Account"),
        ("Other", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("On Hold", "On Hold"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="Other"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Open"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    resolved_on = models.DateTimeField(
        null=True,
        blank=True
    )

    attachment = models.FileField(
        upload_to="ticket_attachments/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class Comment(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ticket.title}"

class TicketHistory(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="history",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    action = models.CharField(max_length=100)

    details = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["-created"]

    def __str__(self):

        return f"{self.ticket} - {self.action}"
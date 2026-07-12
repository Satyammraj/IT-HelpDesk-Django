from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'title',
        'category',
        'priority',
        'status',
        'created',
    )

    list_filter = (
        'status',
        'priority',
        'category',
    )

    search_fields = (
        'title',
        'description',
    )

    ordering = ('-created',)
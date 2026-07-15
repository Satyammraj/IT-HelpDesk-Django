from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("create-ticket/", views.create_ticket, name="create_ticket"),
    path("edit/<int:ticket_id>/", views.edit_ticket, name="edit_ticket"),
    path("close/<int:ticket_id>/", views.close_ticket, name="close_ticket"),
    path("delete/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),
    path("ticket/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path("ticket/<int:ticket_id>/status/", views.update_status, name="update_status"),
    path("test-email/", views.test_email, name="test_email"),
    
]

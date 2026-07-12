from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings, name="settings"),
    path("users-list/", views.users_list, name="users_list"),
    path("toggle-admin/<int:user_id>/", views.toggle_admin, name="toggle_admin"),
    path("register/", views.register, name="register"),
]

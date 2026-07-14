from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import (
    RegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
)

# -------------------------
# Logout
# -------------------------


def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------------
# Register
# -------------------------


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Account created successfully. Please log in.")

            return redirect("login")

    else:

        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


# -------------------------
# Profile
# -------------------------


@login_required
def profile(request):

    if request.method == "POST":

        user_form = UserUpdateForm(request.POST, instance=request.user)

        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )


        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()

            profile_form.save()

            messages.success(request, "Profile updated successfully!")

            return redirect("profile")

    else:

        user_form = UserUpdateForm(instance=request.user)

        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        "users/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


# -------------------------
# Settings
# -------------------------

@login_required
def settings(request):

    profile = request.user.profile

    if request.method == "POST":

        profile.theme = request.POST.get("theme")

        profile.email_notifications = request.POST.get("email_notifications") == "on"

        profile.save()

        profile.refresh_from_db()

        messages.success(request, "Settings updated successfully.")

        return redirect("settings")

    return render(
        request,
        "users/settings.html",
        {
            "profile": profile,
        },
    )


# -------------------------
# Users List
# -------------------------


@login_required
def users_list(request):

    if not request.user.is_staff:
        return redirect("dashboard")

    users = User.objects.all().order_by("username")

    return render(request, "users/users_list.html", {"users": users})


# -------------------------
# Toggle Admin
# -------------------------


@login_required
def toggle_admin(request, user_id):

    if not request.user.is_staff:
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    if user != request.user:

        user.is_staff = not user.is_staff

        user.save()

    return redirect("users_list")

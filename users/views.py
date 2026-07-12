from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import RegisterForm
from django.contrib.auth import login

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def profile(request):
    return render(request, 'users/profile.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def settings(request):
    return render(request, 'users/settings.html')

@login_required
def users_list(request):

    if not request.user.is_staff:
        return redirect("dashboard")

    users = User.objects.all().order_by("username")

    return render(
        request,
        "users/users_list.html",
        {
            "users": users
        }
    )


@login_required
def toggle_admin(request, user_id):

    if not request.user.is_staff:
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    # Don't let an admin remove their own admin rights
    if user != request.user:
        user.is_staff = not user.is_staff
        user.save()

    return redirect("users_list")

def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(form.cleaned_data["password"])

            user.save()

            login(request, user)

            return redirect("dashboard")

    else:

        form = RegisterForm()

    return render(

        request,

        "registration/register.html",

        {

            "form": form

        }

    )
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

from apps.main.models import Category

def login_views(request):
    if request.user.is_authenticated:
        return redirect("main:post_list")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect("main:post_list")

    return render(request, 'accounts/login.html', {"form": form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("main:post_list")
    
    form = UserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("main:post_list")

    return render(request, 'accounts/register.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect("main:post_list")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")
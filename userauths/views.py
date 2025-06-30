from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from userauths.models import Profile, User
import re
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Hey, you are already logged in.")
        return redirect("studio:home")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "").strip()

        if not identifier or not password:
            messages.error(request, "Please fill in all required fields")
            return redirect("userauths:sign-in")

        try:
            # Try to find user by phone, email, or username
            if identifier.isdigit():  # Phone number
                user = User.objects.get(phone=identifier)
                auth_user = authenticate(request, phone=identifier, password=password)
            elif '@' in identifier:  # Email
                user = User.objects.get(email=identifier)
                auth_user = authenticate(request, email=identifier, password=password)
            else:  # Username
                user = User.objects.get(username=identifier)
                auth_user = authenticate(request, username=identifier, password=password)
            
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, f"Welcome back, {auth_user.username}!")
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else "studio:home")
            else:
                messages.error(request, "Invalid credentials")
                
        except User.DoesNotExist:
            messages.error(request, "Account not found")
        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")

    return render(request, "userauths/sign-in.html")
    
@csrf_protect
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            phone = form.cleaned_data.get("phone")
            
            # Authenticate with phone (USERNAME_FIELD)
            auth_user = authenticate(
                request,
                phone=phone,
                password=form.cleaned_data['password1']
            )
            
            if auth_user:
                login(request, auth_user)
                messages.success(request, f"Welcome {username}! Your account was created successfully.")
                return redirect("studio:home")
            else:
                messages.error(request, "Authentication failed after registration")
    else:
        form = UserRegisterForm()

    return render(request, "userauths/sign-up.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You logged out.")
    return redirect("userauths:sign-in")


def profile_update(request):
    """
    Handles updating of user profile.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("studio:home")  # Redirect to dashboard after successful update
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }
    return render(request, "userauths/profile-edit.html", context)

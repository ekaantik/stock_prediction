from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            # check if the username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is taken. Please choose another one.")
                messages.error(request, form.errors)
            # check if the email already exists
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use.")
                messages.error(request, form.errors)
            else:
                # validate the password strength
                try:
                    validate_password(password)
                except Exception as e:
                    messages.error(request, e)
                else:
                    # create the new user
                    form.save()
                    messages.success(request, "Registration successful. Please Login from here!")
                    return redirect("accounts:login")
        else:
            messages.error(request, "Invalid information. Please try again.")
            messages.error(request, form.errors)
    form = NewUserForm()
    return render(request=request, template_name="accounts/register.html", context={"form":form})

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # login(request)
                    messages.success(request, f"Welcome back, {username}. You are now logged in.")
                    return redirect("accounts:home")
                else:
                    messages.error(request, "Your account is not active.")
                    messages.error(request, form.errors)
            else:
                # if username or password is incorrect
                messages.error(request, "Invalid username or password.")
                messages.error(request, form.errors)
        else:
            # if the form is not valid
            messages.error(request, "Invalid username or password.")
            messages.error(request, form.errors)
    form = AuthenticationForm()
    return render(request=request, template_name="accounts/login.html", context={"form":form})

def Logout(request):
    return render(request,'accounts/logout.html')
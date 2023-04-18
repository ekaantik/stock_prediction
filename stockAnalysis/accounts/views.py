from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            # check if the username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is taken. Please choose another one.")
            # check if the email already exists
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use.")
            else:
                # create the new user
                form.save()
                messages.success(request, "Registration successful.")
                return redirect("accounts:login")
        else:
            messages.error(request, "Invalid information. Please try again.")
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
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("accounts:home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="accounts/login.html", context={"form":form})

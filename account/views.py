from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, UserLoginForm



def signup_page(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            
            return redirect('login')  # Replace 'home' with your desired redirect URL after signup
    else:
        form = SignUpForm()
    
    context = {'form': form}
    return render(request, 'account/signup.html', context)

def login_page(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('home')  # Replace 'home' with your desired redirect URL after login
            else:
                form.add_error(None, 'Invalid email or password. Please try again.') 
    else:
        form = UserLoginForm()

    context = {
        'form': form
        }
    return render(request, 'account/login.html', context)

def logout_page(request):
    logout(request)
    return redirect('/signup/login/')  # Replace 'home' with the name of your home URL


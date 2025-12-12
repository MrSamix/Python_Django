from django.shortcuts import render, redirect
from .models import User

# DIRECTORY_NAME = 'users'

# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password = hash(password)
        
        user = User.objects.filter(username=username, password=password).first()

        userEmail = User.objects.filter(email=username, password=password).first()

        if user is not None or userEmail is not None:
            return redirect('/')
        else:
            
            return render(request, 'login.html', {'error': 'Невірні дані'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeatPassword')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        if password != repeat_password:
            return render(request, 'register.html', {'error': 'Паролі не співпадають'})
        
        if username and password and firstname and lastname and email:
            user = User(
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=hash(password),
                image=image
            )
            user.save()
            return redirect('login')
        else:
            return render(request, 'register.html', {'error': 'Заповніть всі поля'})
    return render(request, 'register.html')



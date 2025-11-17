from django.shortcuts import render

DIRECTORY_NAME = 'users'

# Create your views here.
def index(request):
    return render(request, f'{DIRECTORY_NAME}/home.html')

def login(request):
    return render(request, f'{DIRECTORY_NAME}/login.html')

def register(request):
    return render(request, f'{DIRECTORY_NAME}/register.html')
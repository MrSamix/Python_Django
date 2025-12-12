from django.shortcuts import render
from .models import Category

# Create your views here.

def show_categories(request):
    categories = Category.objects.all()
    return render(request, "categories.html", {'categories': categories})

def add_category(request):
    return render(request, 'add_category.html')
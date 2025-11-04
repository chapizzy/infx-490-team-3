from django.shortcuts import render

# Home page view
def home(request):
    return render(request, "ui/home.html")

# What is FoodLens page view
def what_is_foodlens(request):
    return render(request, "ui/what_is_foodlens.html")
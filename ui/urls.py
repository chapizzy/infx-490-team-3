from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('what-is-foodlens/', views.what_is_foodlens, name='what_is_foodlens'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]

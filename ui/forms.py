from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email') # You can add more fields if needed

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

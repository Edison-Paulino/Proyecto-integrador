from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Requerido. Introduce una dirección de correo válida.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True, help_text='Requerido. Introduce tu nombre de usuario.')
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text='Requerido. Introduce tu contraseña.')

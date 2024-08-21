from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .forms import RegisterForm

def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirige a la página principal después de iniciar sesión
        else:
            error_message = "Nombre de usuario o contraseña incorrectos"

    return render(request, 'login.html', {'error_message': error_message})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Autenticar y loguear automáticamente
            user = authenticate(request, username=user.username, password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('/')
        else:
            return render(request, 'register.html', {'form': form})
    
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import ToDoForm
from .models import Todo
# Create your views here.


def home(request):
    return render(request, "todo/home.html")


def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signupuser.html', {"form": UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:

            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user=user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {"form": UserCreationForm(), "error": "This username is already taken!"})

        else:
            return render(request, 'todo/signupuser.html',
                          {"form": UserCreationForm(), "error": "Passwords did not match!"})


def loginuser(request):
    if request.method == "GET":
        return render(request, 'todo/loginuser.html', {"form": AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if not user:
            return render(request, 'todo/loginuser.html',
                          {"form": AuthenticationForm(), "error": "Incorrect password or username"})
        login(request, user=user)
        return redirect('currenttodos')


@login_required()
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')


@login_required()
def createtodo(request):
    if request.method == "GET":
        return render(request, 'todo/createtodo.html', {"form": ToDoForm()})
    else:
        try:
            form = ToDoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html',
                          {"form": ToDoForm(), "error": "Bat data passed in. Try again."})


@login_required()
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, "todo/currenttodos.html", {"todos": todos})


@login_required()
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, "todo/completedtodos.html", {"todos": todos})


@login_required()
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    form = ToDoForm(instance=todo)
    # Viewing todo
    if request.method == "GET":
        return render(request, "todo/viewtodo.html", {"todo": todo, "form": form})
    else:
        # Editing todo
        try:
            form = ToDoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, "todo/viewtodo.html",
                          {"todo": todo, "form": form, "error": "Bat data passed in. Try again."})


@login_required()
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required()
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreatePollForm, CreateUserForm
from .models import Poll
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')
    context = {'form' : form}
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password  = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
           messages.info(request, 'Username or password is incorrect')
    context = {}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


def home(request):
    polls = Poll.objects.all()
    context = {'polls':polls}
    return render(request, 'accounts/main.html', context)

@login_required(login_url='login')
def create(request):
    if request.method == 'POST':
        form = CreatePollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CreatePollForm()
    context = {'form':form}
    return render(request, 'accounts/create.html', context)

@login_required(login_url='login')
def results(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    context = {'poll':poll}
    return render(request, 'accounts/results.html', context)

@login_required(login_url='login')
def vote(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)

    if request.method == 'POST':

        selected_option = request.POST['poll']
        if selected_option == 'option1':
            poll.option_one_count += 1
        elif selected_option == 'option2':
            poll.option_two_count += 1
        elif selected_option == 'option3':
            poll.option_three_count += 1
        else:
            return HttpResponse(400, 'Invalid form')

        poll.save()

        return redirect('results', poll.id)

    context = {
        'poll' : poll
    }
    return render(request, 'accounts/vote.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def delete(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    if request.method == "POST":
        poll.delete()
        return redirect('/')
    context = {'poll': poll}
    return render(request, 'accounts/delete.html', context)


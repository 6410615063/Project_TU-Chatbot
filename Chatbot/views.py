from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from . import chat
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import Profile, Chat

# Create your views here.

# def main_2(request) :
# # def main(request) :
#     current_chat = 'TestChat'
#     return render(request, 'grid.html', {
#         # "chatlog": chat.get_chatlog()
#         # "chatlog": chat.get_chatlog_2()
#         # "chatlog": chat.get_chatlog_3()
#         "chatlog": chat.get_chatlog_4('TestUser', current_chat)
#         , "authenticated": request.user.is_authenticated
#         , 'chats': chat.get_chats('TestUser')
#         , 'current_chat': current_chat
#     })

# handle User and Guest differently
# def main_2(request) :
def main(request) :
    isLoggedIn = request.user.is_authenticated
    context = {
        "authenticated": isLoggedIn
    }
    if (isLoggedIn) :
        # user
        user = request.user
        current_chat = request.session.get('current_chat', 'TestChat')

        context['current_chat'] = current_chat
        context['chatlog'] = chat.get_chatlog_6(user, current_chat) # need to make a new func that take User obj
        context['chats'] = chat.get_chats_2(user) # need to make a new func that take User obj
    else :
        # guest
        
        context['current_chat'] = 'Insert Chat name here'
        context['chatlog'] = request.session.get('chatlog', ["Hello, how can I help you?"])
    return render(request, 'grid.html', context)

# currently only work if logged in
def send_msg(request) :
    user_message = request.POST['input_msg']
    user = request.user
    current_chat = request.session.get('current_chat', 'TestChat')

    # chat.user_chat(user_message)
    chat.user_chat(user, current_chat, user_message)
    return redirect('main')

def send_msg2(request) :
    isLoggedIn = request.user.is_authenticated
    user_message = request.POST['input_msg']

    if (isLoggedIn) :
        # user
        user = request.user
        current_chat = request.session.get('current_chat', 'TestChat')

        chat.user_chat(user, current_chat, user_message)
    else :
        # guest
        chatlog = request.session.get('chatlog', ["Hello, how can I help you?"])
        
        new_chatlog = chat.guest_chat(chatlog, user_message)

        request.session['chatlog'] = new_chatlog
    return redirect('main')

def refresh_chat(request) :
    chat.reset()
    return redirect('main')

def change_chat(request, chat_name) :
    # call a function that change a value?
    request.session['current_chat'] = chat_name
    
    return redirect('main')

def create_chat(request) :
    user = request.user
    # make new chat
    chat_name = chat.create_chat(user)
    # assign new chat as current chat
    request.session['current_chat'] = chat_name

    return redirect('main')

def delete_chat(request, chat_name) :
    # call function to delete chat
    # update current_chat -> find a new chat?
    user = request.user
    delete_result = chat.delete_chat(user, chat_name)

    if delete_result != '' :
        request.session['current_chat'] = delete_result
        return redirect('main')
    else :
        return redirect('create_chat')

def login_user(request) :
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
    
            return redirect('main')

    return render(request, 'login.html')

def login_user_test(request) :
    username = 'TestUser'
    password = 'tset12345'

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    
    return redirect('main')

def logout_user(request) :
    logout(request)

    return redirect('main')

def test_form(request) :

    return render(request, 'test_form.html')


def create_user(request) :
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)
        profile = Profile(
            user = user
        )
        profile.save()
        # make new chat
        chat.create_chat(user)


        print(f"User '{username}' created")
    
        return redirect('main')
    else :
        return render(request, 'create_user.html')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from . import chat
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import Profile, Chat
# for line chatbot
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from .line_chatbot import get_stateless_access_token, handle_messages, reply

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

# for handling POST request from Line chatbot
@csrf_exempt
def linebot_test(request) :
    # list of thing this function should do
    # 1. check that the request is from Line via the 'x-line-signature' (Signature validation)
    # 2. read request body for messages
    #   2.1 get the reply token
    #   2.2 check if the body is JSON or text
    #       Yes -> extract the messages -> prepare to send the messages back as a reply (actually need to make a query to LLM using the messages)
    #       No -> ask user to send a JSON or text message
    # extra: save the request body to a file for debugging
    # 3. send a reply back to the user
    #   3.1 request a channel access token
    #   3.2 prepare the reply message
    #   3.3 send the reply message back to the user

    # 1. check that the request is from Line via the 'x-line-signature' (Signature validation)
    content_type = request.headers.get('Content-Type')

    # extra: save the request body to a file for debugging
    filename = "most_recent_request_body.json"
    with open(filename, 'w') as file:
        # TODO: need to verify if the request is from Line via the 'x-line-signature' (Signature validation)
        # if content_type == "application/json" :
        #     content = json.loads(request.body)
        #     json.dump(content, file, indent=4)
        # elif content_type.find("text") != -1 :
        #     file.write(request.body.decode('utf-8'))
        # else :
        #     file.write("The most recent request contain neither text nor JSON body")

        content = json.loads(request.body)
        # just write the entire body
        # json.dump(content, file, indent=4)

        # get reply token


        reply_token = "" 
        # write only text message
        texts = []
        events = content['events']
        for event in events :
            if event['type'] == "message" :
                message = event['message']
                if message['type'] == "text" :
                    text = message['text']
                    texts.append(text)
                    reply_token = event['replyToken']
        texts_display = "\n".join(texts)
        display = f"""
Received messages:\n
{texts_display}
"""
        file.write(display)

        # as a test, just repeat the messages back to user
        # sending a reply via a curl request

        # get channel access token by making a request
        channel_access_token = "" # (stateless access token)
        url = "https://api.line.me/oauth2/v3/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": "2006964670",
            "client_secret": "6df7929b42d1564564214ef8ecd2f0d8"
        }

        # make the POST request (replicating --data-urlencode in curl by using 'params')
        response = requests.post(url, headers=headers, params=data)

        # Check the response status code
        if response.status_code == 200:
            response_json = response.json()
            channel_access_token = response_json['access_token']
        else:
            print(f"Request failed with status code {response.status_code} and response: {response.text}")

        messages = [
            {
                "type": "text"
                , "text": "Are these your message?"
            }
            , {
                "type": "text"
                , "text": display
            }
        ]

        # url, header, and body
        url = "https://api.line.me/v2/bot/message/reply"
        headers = {
            "Authorization": f"Bearer {channel_access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "replyToken": reply_token,
            "messages": messages,
        }

        # Make the POST request
        response = requests.post(url, headers=headers, json=data)
        

    return HttpResponse("test string", status=200)


# for handling POST request from Line chatbot
@csrf_exempt
def linebot_test2(request) :
    # 1. check that the request is from Line via the 'x-line-signature' (Signature validation)
    content_type = request.headers.get('Content-Type')
    # 2. read request body for messages
    content = json.loads(request.body)
    #   2.1 get the reply token
        # currently dont know if event['type'] != "message" also have replyToken or not -> need to test later
    reply_token = "" 
    #   2.2 check if the body is a text message
    #       Yes -> extract the messages -> prepare to send the messages back as a reply (actually need to make a query to LLM using the messages)
    #       No -> ask user to send a text message
        # extract only text message
    texts = []
    events = content['events']
    for event in events :
        if event['type'] == "message" :
            reply_token = event['replyToken']
            message = event['message']
            if message['type'] == "text" :
                text = message['text']
                texts.append(text)
    texts_display = "\n".join(texts)
    display = f"""
Received messages:\n
{texts_display}
"""
    # extra: save the request body to a file for debugging
    filename = "most_recent_request_body.json"
    with open(filename, 'w') as file:
        file.write(display)
    # 3. send a reply back to the user
    #   3.1 request a channel access token
    channel_access_token = get_stateless_access_token()
    #   3.2 prepare the reply message
    messages = handle_messages(texts)
    #   3.3 send the reply message back to the user
    reply(channel_access_token, reply_token, messages)
    
        # send a 200 response back to Line to confirm that the message has been received
    return HttpResponse("test string", status=200)
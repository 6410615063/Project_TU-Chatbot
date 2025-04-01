from . import chatbot
from .models import Profile, Chat
from django.contrib.auth.models import User

chatlog = []
# # get chat from the list above
# def get_chatlog() :
#     if (len(chatlog) == 0) :
#         #chatlog.append("Hello, how can I help you?")
#         chatlog.append({"role": "assistant", "content": "Hello, how can I help you?"})
#     chatlog_content = [message["content"] for message in chatlog]
#     return chatlog_content

# # get chat from a specific obj of the Chat model in the DB
# def get_chatlog_2() :
#     chat = Chat.objects.get(name='TestChat')
#     chat_content = [message["content"] for message in chat.messages]
#     return chat_content

# # get user -> profile -> chat -> message, but fixed user
# def get_chatlog_3() :
#     user = User.objects.get(username='TestUser')
#     profile = user.profile
#     chats = profile.chats.all()
#     chat = chats[0]
#     chat_content = [message["content"] for message in chat.messages]
#     return chat_content

# # like get_chatlog_3, but from given user & chat name
# def get_chatlog_4(user_name, chat_name) :
#     user = User.objects.get(username=user_name)
#     profile = user.profile
#     chats = profile.chats.all()

#     # get the user's chat based on given name
#     filtered_chats = [chat for chat in chats if chat.name == chat_name]
#     if len(filtered_chats) == 1 :
#         chat = filtered_chats[0]
#     else :
#         chat = chats[0]
    
#     chat_content = [message["content"] for message in chat.messages]
#     return chat_content

# def get_chatlog_5(user, chat_name) :
#     profile = user.profile
#     chats = profile.chats.all()

#     # get the user's chat based on given name
#     filtered_chats = [chat for chat in chats if chat.name == chat_name]
#     if len(filtered_chats) == 1 :
#         chat = filtered_chats[0]
#         print('chat found')
#     else :
#         chat = chats[0]
#         print('chat not found')
    
#     chat_content = [message["content"] for message in chat.messages]
#     return chat_content

def get_chatlog_6(user, chat_name) :
    profile = user.profile
    chats = profile.chats.all()

    # get the user's chat based on given name
    filtered_chats = chats.filter(name=chat_name)
    if filtered_chats.count() == 1 :
        chat = filtered_chats[0]
        print('chat found')
    else :
        chat = chats[0]
        print('chat not found')
    
    chat_content = [message["content"] for message in chat.messages]
    return chat_content

# def get_chats(user_name) :
#     user = User.objects.get(username=user_name)
#     profile = user.profile
#     chats = profile.chats.all()
#     chat_name = [chat.name for chat in chats]

#     return chat_name

# format chatlog for displaying
def get_chats_2(user) :
    profile = user.profile
    chats = profile.chats.all()
    chat_name = [chat.name for chat in chats]

    return chat_name

def create_chat(user) :
    profile = user.profile
    chats = profile.chats.all()

    # come up with a unique new name
    new_name = 'New Chat'
    number = 0
    while(chats.filter(name=new_name).exists()) :
        number += 1
        new_name = f'New Chat{number}'

    # make new chat & attatch it to profile
    new_chat = Chat(
        name = new_name
        , profile = profile
        , messages = [
            {"role": "assistant", "content": "Hello, how can I help you?"}
            ]
    )
    new_chat.save()

    return new_name

def delete_chat(user, chat_name) :
    profile = user.profile
    chats = profile.chats.all()

    # get the user's chat based on given name
    filtered_chats = chats.filter(name=chat_name)
    if filtered_chats.count() == 1 :
        chat = filtered_chats[0]
        chat.delete()
        print('delete_chat: chat found')
    else :
        chat = chats[0]
        print('delete_chat: chat not found')

    chats = profile.chats.all()
    if chats.count() > 0 :
        return chats[0].name
    else :
        return ''

def append_chatlog(message) :
    chatlog.append(message)

def user_chat(message) :
    # add user message to log
    append_chatlog({"role": "user", "content": message})

    # generate chatbot's message
    chatbot_message = chatbot.generate_chatbot_message(chatlog, "claude-haiku")

    # add user message to log
    append_chatlog({"role": "assistant", "content": chatbot_message})

def user_chat(user, chat_name, message) :
    profile = user.profile
    chats = profile.chats.all()

    # get the user's chat based on given name
    filtered_chats = chats.filter(name=chat_name)
    if len(filtered_chats) == 1 :
        chat = filtered_chats[0]
        print('user_chat: chat found')
    else :
        chat = chats[0]
        print('user_chat: chat not found')
    
    chatlog = chat.messages
    # add user message to log
    chatlog.append({"role": "user", "content": message})

    # generate chatbot's message
    chatbot_message = chatbot.generate_chatbot_message(chatlog, "claude-haiku")

    # add user message to log
    chatlog.append({"role": "assistant", "content": chatbot_message})

    chat.messages = chatlog
    chat.save()

def guest_chat(chats, message) :
    # chatbot is in the format ['msg1', 'msg2', 'msg3', ...]
    # need to change into [{'role': 'assistant', 'context': 'msg1}, {'role': 'user', 'context': 'msg2}, ...]
    chat_count = len(chats)
    chatlog = []
    for i in range(chat_count) :
        if (i % 2 == 0) :
            # assistant's
            chatlog.append({"role": "assistant", "content": chats[i]})
        else :
            # guest's
            chatlog.append({"role": "user", "content": chats[i]})

    # add user message to log
    chatlog.append({"role": "user", "content": message})

    # generate chatbot's message
    chatbot_message = chatbot.generate_chatbot_message(chatlog, "claude-haiku")
    
    # add user message to log
    chatlog.append({"role": "assistant", "content": chatbot_message})

    # format for displaying
    chatlog_display = [message['content'] for message in chatlog]

    return chatlog_display

def reset() :
    chatlog.clear()
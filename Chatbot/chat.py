from . import chatbot
from .models import Profile, Chat
from django.contrib.auth.models import User

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

    # prepare chatlog for displaying
    chat_content = [message["content"] for message in chat.messages]
    return chat_content

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

def user_chat(user, chat_name, message_new) :
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
    chatlog.append({"role": "user", "content": message_new})

    # TODO: need to make sure that no message is empty
    # this currently actually impacted the recorded chatlog
    for message in chatlog :
        if message['content'] == '' :
            message['content'] = '-'

    # generate chatbot's message
    chatbot_message = chatbot.generate_chatbot_message(chatlog, "claude-haiku")

    # add user message to log
    chatlog.append({"role": "assistant", "content": chatbot_message})

    chat.messages = chatlog
    chat.save()

def guest_chat(chats, message_new) :
    # chatbot is in the format ['msg1', 'msg2', 'msg3', ...]
    # need to change into [{'role': 'assistant', 'context': 'msg1}, {'role': 'user', 'context': 'msg2}, ...]
    chat_count = len(chats)
    chatlog = []
    for i in range(chat_count) :
        # handle empty message
        # this currently does not impacted the recorded chatlog
        message = chats[i]
        if message == '' :
            message = '-'

        if (i % 2 == 0) :
            # assistant's
            chatlog.append({"role": "assistant", "content": message})
        else :
            # guest's
            chatlog.append({"role": "user", "content": message})

    # add user message to log
    chatlog.append({"role": "user", "content": message_new})

    # generate chatbot's message
    chatbot_message = chatbot.generate_chatbot_message(chatlog, "claude-haiku")

    # add user message to log
    chatlog.append({"role": "assistant", "content": chatbot_message})

    # format for displaying
    chatlog_display = [message['content'] for message in chatlog]

    return chatlog_display

def refresh_chat(user, chat_name) :
    profile = user.profile
    chats = profile.chats.all()

    # get the user's chat based on given name
    filtered_chats = chats.filter(name=chat_name)
    if filtered_chats.count() == 1 :
        chat = filtered_chats[0]
        print('refresh_chat: chat found')
    else :
        chat = chats[0]
        print('refresh_chat: chat not found')

    chat.messages = [
            {"role": "assistant", "content": "Hello, how can I help you?"}
            ]
    chat.save()

def delete_msg(user, chat_name, index) :
    profile = user.profile
    chats = profile.chats.all()

    # get the user's chat based on given name
    filtered_chats = chats.filter(name=chat_name)
    if filtered_chats.count() == 1 :
        chat = filtered_chats[0]
        print('delete_msg: chat found')
    else :
        chat = chats[0]
        print('delete_msg: chat not found')

    # delete all message from index to end
    chatlog = chat.messages[:index-1]
    print(chatlog)

    # save changes to database
    chat.messages = chatlog
    chat.save()
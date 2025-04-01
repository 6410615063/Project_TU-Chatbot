import requests
from .chatbot import generate_chatbot_message

# get a stateless channel access token by making a request to the LINE API
def get_stateless_access_token() :
        channel_access_token = ""
        url = "https://api.line.me/oauth2/v3/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # TODO: need to put client_id and client_secret in a more secure place (JSON file, environment variables, etc.)
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

        return channel_access_token

# from a list of incoming msg from Line user, create a reply JSON
def handle_messages(messages_list) :
    messages_text = "\n".join(messages_list)
    
    reply = [
        {
            "type": "text"
            , "text": "Are these your message?"
        }
        , {
            "type": "text"
            , "text": messages_text
        }
    ]

    return reply

# try using LLM to generate a response
def handle_messages2(messages_list) :
    messages_text = "\n".join(messages_list)

    context = [
         {
            "role": "user",
            "content": messages_text
         }
    ]

    reply_text = generate_chatbot_message(context, "claude-haiku")

    reply = [
         {
            "type": "text"
            , "text": reply_text
        }
    ]

    return reply

def reply(channel_access_token, reply_token, reply) :
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "replyToken": reply_token,
        "messages": reply,
    }

        # Make the POST request to reply
    requests.post(url, headers=headers, json=data)
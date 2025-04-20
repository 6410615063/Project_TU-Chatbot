import requests
from Chatbot.chatbot import generate_chatbot_message
from security_model.model import SecurityModel

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
            "client_id": "2007171252",
            "client_secret": "67f8d5d012975e0319a8d2c1a7c46050"
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
    
    # ตรวจสอบความปลอดภัยของข้อความ
    security_model = SecurityModel()
    if not security_model.load_model():
        security_model.train()
    
    # ตรวจสอบแต่ละข้อความ
    for message in messages_list:
        if security_model.predict(message) == "unsafe":
            return [
                {
                    "type": "text",
                    "text": "ไม่สามารถตอบคำถามของคุณได้"
                }
            ]

    context = [
         {
            "role": "user",
            "content": messages_text
         }
    ]

    reply_text = generate_chatbot_message(context, "gemini-2.5-pro-exp-03-25")

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

    try:
        # Make the POST request to reply
        response = requests.post(url, headers=headers, json=data)
        print("Line API Response Status:", response.status_code)
        print("Line API Response Body:", response.text)
        
        if response.status_code != 200:
            print(f"Error: Line API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            # ถ้า token หมดอายุ ให้ขอ token ใหม่
            if response.status_code == 401:
                new_token = get_stateless_access_token()
                if new_token:
                    # อัพเดท token ใน .env
                    with open('.env', 'r') as f:
                        lines = f.readlines()
                    with open('.env', 'w') as f:
                        for line in lines:
                            if not line.startswith('LINE_CHANNEL_ACCESS_TOKEN='):
                                f.write(line)
                        f.write(f'LINE_CHANNEL_ACCESS_TOKEN={new_token}\n')
                    # ลองส่งข้อความอีกครั้งด้วย token ใหม่
                    headers["Authorization"] = f"Bearer {new_token}"
                    response = requests.post(url, headers=headers, json=data)
                    print("Retry with new token - Status:", response.status_code)
                    print("Retry with new token - Response:", response.text)
    except Exception as e:
        print(f"Error sending reply: {str(e)}")

# รับ access token
channel_access_token = get_stateless_access_token()

# อ่านค่า API keys จาก .env ถ้ามี
google_api_key = ""
pinecone_api_key = ""
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GOOGLE_API_KEY='):
                google_api_key = line.strip()
            elif line.startswith('PINECONE_API_KEY='):
                pinecone_api_key = line.strip()
except FileNotFoundError:
    pass

# นำค่าไปใส่ใน .env
with open('.env', 'w') as f:
    f.write(f'LINE_CHANNEL_ACCESS_TOKEN={channel_access_token}\n')
    if google_api_key:
        f.write(f'{google_api_key}\n')
    if pinecone_api_key:
        f.write(f'{pinecone_api_key}\n')
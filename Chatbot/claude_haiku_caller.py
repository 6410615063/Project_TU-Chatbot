from google.oauth2 import service_account
import requests
import google.auth.transport.requests
import json
from django.conf import settings
from pathlib import Path

# response -> message
def convert(response) :
    response_string = response.text
    response_list = response_string.split("\n\n")
    response_msg_list = []
    for response in response_list :
        #split 'event' and 'data'
        response_headers = response.split("\n")
        event_header = response_headers[0]
        event = event_header.removeprefix("event: ")
        if event == "content_block_delta" :
            data_header = response_headers[1]
            data = data_header.removeprefix("data: ") #is a json string
            data_json = json.loads(data)
            text = data_json['delta']['text']
            response_msg_list.append(text)

    response_message = "".join(response_msg_list)
    return response_message

def generate() :
    return "Insert message from claude-haiku API here"

def generate(context) :
    # Path to credentials JSON file
    service_account_file = Path(settings.BASE_DIR, "static/cn408-homework-012d7d8cf8a6.json")  # Ensure this path is correct

    # Define the required scopes
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    # Load the service account credentials with the specified scopes
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)

    # Create a request object
    request = google.auth.transport.requests.Request()

    # Refresh the credentials to get the access token
    credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Plan - make a curl request to vertex api
    url = "https://us-central1-aiplatform.googleapis.com/v1/projects/cn408-homework/locations/us-central1/publishers/anthropic/models/claude-3-haiku@20240307:streamRawPredict"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "anthropic_version": "vertex-2023-10-16",
        "system": "You are a chatbot of the faculty of engineering of Thammasat university. Your job is to answer question related to the faculty. Your answer should be short",
        "messages": context,
        "max_tokens": 300,
        "stream": True
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=data)

    # Check the response status code
    if response.status_code == 200:
        message = convert(response)
        return message
    else:
        print(f"Request failed with status code {response.status_code} and response: {response.text}")
        return "Error happend, check terminal"
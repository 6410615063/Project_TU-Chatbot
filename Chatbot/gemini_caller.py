import google.generativeai as genai
import os
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please add it to your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

def generate(context):
    try:
        # Convert context to the format expected by Gemini
        messages = []
        for msg in context:
            if msg['role'] == 'user':
                messages.append(msg['content'])
        
        # Generate response
        response = model.generate_content(messages)
        return response.text
        
    except Exception as e:
        print(f"Error in generate function: {str(e)}")
        return "Sorry, I'm having trouble connecting to the AI service right now." 
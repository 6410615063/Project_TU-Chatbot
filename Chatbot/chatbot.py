from Chatbot.gemini_caller import generate as gemini_generate
from Chatbot.rag_handler import RAG_response

def generate_chatbot_message(context, model_name):
    # Get the user's message from context
    user_message = context[0]['content']
    
    # Use RAG to generate response
    reply_text = RAG_response(user_message)
    return reply_text

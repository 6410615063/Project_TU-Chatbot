from anthropic import AnthropicVertex # for claude API
import os # for fetching value from venv?
from . import claude_haiku_caller

def generate_chatbot_message(context, option='default') :
    if option == "claude-haiku" :
        # return claude_haiku_caller.generate(context)
        return claude_haiku_caller.check_then_generate(context)
    elif option == "claude-sonnet" :
        return "Insert message from claude-sonnet API here"
    elif option == "context" :
        return context
    else :
        return "I'm sorry, could you say that again?"
# test_agent.py

import openai
import os
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

# Get your API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Talk to the OpenAI model
def chat_with_gpt(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # use "gpt-4" if you have access
        messages=[
            {"role": "system", "content": "You are a helpful scholarship assistant."},
            {"role": "user", "content": message}
        ]
    )
    reply = response['choices'][0]['message']['content']
    return reply

# Try it out
if __name__ == "__main__":
    user_input = input("Ask me something about scholarships: ")
    reply = chat_with_gpt(user_input)
    print(" ScholarBot:", reply)

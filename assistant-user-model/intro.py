import openai
import os
from dotenv import load_dotenv, find_dotenv

# Example OpenAI Python library request
MODEL = "gpt-4"
_ = load_dotenv("keys.env")

assistantCont = input("What am I?\t")
userCont = input("What would you like me to do?\t")
openai.api_key = os.environ['OPENAI_API_KEY']
response = openai.ChatCompletion.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a very helpful assistant"},
        {"role": "assistant", "content": assistantCont},
        {"role": "user", "content": userCont},
    ],
    temperature=0.2
)

print(response['choices'][0]['message']['content'])


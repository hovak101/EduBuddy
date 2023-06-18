import openai
import os
from dotenv import load_dotenv, find_dotenv
#import tkinter as tkk
#import interface #tkinter file

## Example OpenAI Python library request
MODEL = "gpt-4"


assistantCont = input("What am I?\t")
userCont = input("What would you like me to do?\t")


_ = load_dotenv("assistant-user-model/keys.env")

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


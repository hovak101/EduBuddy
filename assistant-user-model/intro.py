import openai
import os
from dotenv import load_dotenv, find_dotenv
import tkinter as tkk
import interface #tkinter file

## Example OpenAI Python library request
MODEL = "gpt-4"
_ = load_dotenv("assistant-user-model/keys.env")
openai.api_key = os.environ['OPENAI_API_KEY']
response = openai.ChatCompletion.create(
    model=MODEL,

    #decide which system, assistant to use.

    messages=[
        {"role": "system", "content": "You make history questions"},
        {"role": "assistant", "content": "You are someone that creates question on a given topic"},
        {"role": "user", "content": "Can you create 10 questions on the American Revolutionary War with the answer to each question"},
    ],
    temperature=0
)

print(response['choices'][0]['message']['content'])


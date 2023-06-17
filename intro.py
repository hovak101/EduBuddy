import openai
import os

# Example OpenAI Python library request
MODEL = "gpt-4"
openai.api_key = ""
response = openai.ChatCompletion.create(
    model=MODEL,
    prompt = "Explain the golden ratio?",
    messages=[
        {"role": "user", "content": "Hello!"},
    ],
    temperature=0.2
)

print(response['choices'][0]['message']['content'])
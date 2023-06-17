import openai
import os

# Example OpenAI Python library request
MODEL = "gpt-4"
openai.api_key = "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"
response = openai.ChatCompletion.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "What is the weather in San Jose, California?"},
        
    ],
    temperature=0.2,
)

print(response['choices'][0]['message']['content'])
import os
import openai
from dotenv import load_dotenv, find_dotenv
from llama_index import VectorStoreIndex, SimpleDirectoryReader
import pyperclip

import config
load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']
MODEL = "gpt-4"

def waitAndReturnNewText():
    clipboard = pyperclip.waitForNewPaste()
    return clipboard

def translateText(text):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "assistant", "content": "You are a translator."},
            {"role": "user", "content": "Translate the following text into English and recognize the language: " + text},
        ],
        temperature=0
    )
    return response['choices'][0]['message']['content']

def getTitleFromText(text):
    response = openai.ChatCompletion.create(
        model=MODEL,

        # decide which system, assistant to use.
        # input from user data, yo uask to summarize, it will put assistant as "you are a summarizer..."

        messages=[
            {"role": "assistant", "content": "You are someone that generate titles given texts."},
            {"role": "user", "content": "Given the following text, generate a title from 1 to 19 characters: " + text},
        ],
        temperature=0
    )

    return response['choices'][0]['message']['content']
    
def generateSummaryFromText(text, minimumWords, maximumWords):
    response = openai.ChatCompletion.create(
        model=MODEL,

        # decide which system, assistant to use.
        # input from user data, yo uask to summarize, it will put assistant as "you are a summarizer..."

        messages=[
            {"role": "system", "content": "You are a summary writer."},
            {"role": "assistant", "content": "You are someone that summarizes information on a given topic."},
            {"role": "user", "content": "Summarize the following information in " + str(minimumWords) + " to " + str(maximumWords) + " words: " + text},
        ],
        temperature=0
    )

    return response['choices'][0]['message']['content']

def generateQuizFromText(text, numOfQuestions):
    response = openai.ChatCompletion.create(
        model=MODEL,

        #decide which system, assistant to use.

        messages=[
            {"role": "assistant", "content": "You are someone that creates question on a given topic"},
            {"role": "user", "content": "Create " + str(numOfQuestions) + " questions based off of the following text: " + text},
        ],
        temperature=0
    )

    return response['choices'][0]['message']['content']

def getMultipleChoiceQuiz(prompt, num):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a very helpful quiz maker"},
            {"role": "assistant", "content": f"generate {str(num)} questions with 4 alternatives (1 right, 3 wrong) about {str(prompt)} formatted like this: first line: question, next four lines: alternatives. correct marked with '*' at the end of line. label alternatives 'a.'-'d.' and question '<num>.'"},
            {"role": "user", "content": "Make a" + str(num) + " question quiz about " + prompt},
        ],
        temperature=0.2  
    )
    return(response['choices'][0]['message']['content'])
    


def generateResponseFromFile(file, query):
    # Load data from a file
    documents = SimpleDirectoryReader(input_files=[file]).load_data()
    # Create an index from the loaded documents
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    res = query_engine.query(query)
    return res

def getResponseLengthFromText(text):
    length = len(text)

    if length < 50:
        return length
    
    if length < 1000:
        return length // 5
    
    else:
        return 200; 

def translateAudio(audioFile):
    audio_file = open(audioFile, "rb")
    transcript = openai.Audio.translate("whisper-1", audio_file)
    return transcript.text

def sendGptRequest(prompt, context):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a an assistant that helps user requests based on a given context"},
            {"role": "assistant", "content": "You are given the following context:" + context},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2  
    )
    return(response['choices'][0]['message']['content'])



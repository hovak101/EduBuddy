import time
import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import CSVLoader
from langchain.vectorstores import DocArrayInMemorySearch
# from IPython.display import display, Markdown
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders.excel import UnstructuredExcelLoader
from llama_index import download_loader
from llama_index.readers.schema.base import Document
from apify_client import ApifyClient
import wget
from llama_index import download_loader
from llama_index.readers.schema.base import Document
from langchain.agents.agent_toolkits import create_python_agent
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.tools.python.tool import PythonREPLTool
from langchain.python import PythonREPL
from langchain.chat_models import ChatOpenAI
import json
from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.llms import OpenAI
from langchain import SerpAPIWrapper
from langchain.agents.tools import Tool
from langchain import LLMMathChain
import langchain
import pandas as pd
import numpy as np
import pinecone
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.llms import OpenAI
from langchain import SerpAPIWrapper
from langchain.agents.tools import Tool
from langchain import LLMMathChain
import llama_index
import pyaudio
import wave
from pydub import AudioSegment
from hume import HumeStreamClient
from hume.models.config import LanguageConfig, ProsodyConfig
# import torch
# import cv2
import asyncio
import whisper
_ = load_dotenv("keys.env")
openai.api_key = os.environ['OPENAI_API_KEY']
import pydub
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 20000
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
import wave

# Open the WAV file
with wave.open('output.wav', 'rb') as wf:
    # Get the number of frames and the sample width
    num_frames = wf.getnframes()
    sample_width = wf.getsampwidth()

    # Read the frames from the file
    frames = wf.readframes(num_frames)
    sr = wf.getframerate()
# Convert the frames to a numpy array
audio = np.frombuffer(frames, dtype=np.int16)
start = time.time()
def save_mp3(file, data, sample_rate):
    """Save a numpy array of audio data as an MP3 file."""
    sound = AudioSegment(
        data.tobytes(),
        frame_rate=sample_rate,
        sample_width=data.dtype.itemsize,
        channels=1
    )
    sound.export(file, format="mp3")

# You can then use this function to save a numpy array of audio data as an MP3 file like this:
audio = np.array(audio, dtype=np.int16)

print(len(audio))
# print(audio)
save_mp3('test.mp3', audio[-30000:], sr)

emo = []
# "/content/drive/MyDrive/Hackathon/Recording.m4a"
async def go():
    client = HumeStreamClient(os.environ['HUME_API_KEY'])
    config = ProsodyConfig()
    async with client.connect([config]) as socket:
        # for sample in samples:
            result = await socket.send_file("test.mp3")#.send_text(sample)
            emotions = result
            # print(emotions)
            emo.append(emotions)

# Create an event loop
loop = asyncio.get_event_loop()

# Schedule the `go` coroutine to run
loop.run_until_complete(go())
try:
    emo = emo[0]['prosody']['predictions'][0]['emotions']
except:
    print(emo)
# Close the event loop
loop.close()
print(time.time() - start)
print([key for key in emo if key['score'] > 0.5])

model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("output.wav")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)
# print(mel[20:60])
# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions(fp16 = False)
result = whisper.decode(model, mel, options)
print(result.text)
# Load the model and tokenizer
# model_engine = "text-davinci-002"
# Decode the tokens
# decoded_text = model.decode(np.array(result.tokens, dtype = np.float32))
# print(decoded_text)
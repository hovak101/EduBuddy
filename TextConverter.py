import os
import openai
from dotenv import load_dotenv, find_dotenv
from llama_index import VectorStoreIndex, SimpleDirectoryReader

def convertFileToVector(file):
    _ = load_dotenv(r'key.env')
    openai.api_key = os.environ['OPENAI_API_KEY']
    # Load data from a file
    documents = SimpleDirectoryReader(file).load_data()
    # Create an index from the loaded documents
    index = VectorStoreIndex.from_documents(documents)

convertFileToVector(r'content')

# find python module that shows you which applications your using.
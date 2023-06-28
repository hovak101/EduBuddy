import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# For reading in various file types: 
# For reading pdfs
install('pypdf')

# For reading word documents
install('docx2txt')

# # For image to text generation
# install('torch transformers sentencepiece Pillow')
# install('protobuf')

install('pygetwindow')
install('pywinauto')

install('pyperclip')
install('pillow')
install('screeninfo')

install('pyttsx3')
install('openai')
install('python-dotenv')
install('langchain')
install('numpy')
install('pyaudio')
install('pydub')
install('hume')
install('whisper')
install('websockets')
install('pinecone-client')
install('llama_index')
install('screeninfo')
install('pillow')
install('pyperclip')
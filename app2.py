import streamlit as st
import pafy 
import os
import sys
import time
import requests
from zipfile import ZipFile
from translate import Translator
from googletrans import Translator

st.markdown('# 📝 **Transcriber App**')

bar = st.progress(0)

# Custom functions 

# 2. Retrieving audio file from YouTube video
def get_yt(URL):
    
    video = pafy.new(URL)
  
    bestaudio = video.getbestaudio()
    bestaudio.download()
    st.info('Audio file has been retrieved from YouTube video')
    bar.progress(10)

# 3. Upload YouTube audio file to AssemblyAI
def transcribe_yt():

    current_dir = os.getcwd()

    for file in os.listdir(current_dir):
        if file.endswith(".webm"):
            mp4_file = os.path.join(current_dir, file)
            
    filename = mp4_file
    bar.progress(20)

    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
    headers = {'authorization': api_key}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                            headers=headers,
                            data=read_file(filename))
    audio_url = response.json()['upload_url']
    #st.info('3. YouTube audio file has been uploaded to AssemblyAI')
    bar.progress(30)

    # 4. Transcribe uploaded audio file
    
    endpoint = "https://api.assemblyai.com/v2/transcript"

    json = {
    "audio_url": audio_url
    }

    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    transcript_input_response = requests.post(endpoint, json=json, headers=headers)

    #st.info('4. Transcribing uploaded file')

    bar.progress(40)

    # 5. Extract transcript ID
    transcript_id = transcript_input_response.json()["id"]

    #st.info('5. Extract transcript ID')

    bar.progress(50)

    # 6. Retrieve transcription results
    
    headers = {
        "authorization": api_key,
    }
    transcript_output_response = requests.get(endpoint, headers=headers)

    #st.info('6. Retrieve transcription results')

    bar.progress(60)

    # Check if transcription is complete

    from time import sleep

    while transcript_output_response.json()['status'] != 'completed':
        sleep(10)
        st.warning('Transcription is processing ...')
        transcript_output_response = requests.get(endpoint, headers=headers)
    
    bar.progress(100)

    # 7. Print transcribed text

    st.header('Output')
    st.success(transcript_output_response.json()["text"])

    new_name = 'audio.webm'
    cur_dir = os.getcwd()

    for file in os.listdir(cur_dir):
        if file.endswith('.webm'):
            if file==new_name:
                break
            os.rename(file, new_name)
        

    for file in os.listdir(cur_dir):
        if file.endswith('.webm'):
            os.remove(file)
    

    # 8. Save transcribed text to file

    # Save as TXT file

    yt_txt = open('yt.txt', 'w')
    yt_txt.write(transcript_output_response.json()["text"])
    yt_txt.close()

    # Save as SRT file

    srt_endpoint = endpoint + "/srt"
    srt_response = requests.get(srt_endpoint, headers=headers)
    with open("yt.srt", "w") as _file:
        _file.write(srt_response.text)
    
    zip_file = ZipFile('transcription.zip', 'w')
    zip_file.write('yt.txt')
    zip_file.write('yt.srt')
    zip_file.close()

#Summarizing the data

def summarize(str):             
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
        
    output = query({
        "inputs": str,
    })
    
    st.success(output)

def translate(str):
    translator = Translator()
    translated_text = translator.translate(str, dest='hi')
    st.success(translated_text)
    
#####

# The App

# 1. Read API Key from text file
api_key = st.secrets['api_key']

#st.info('1. API is read ...')
st.warning('Awaiting URL input in the sidebar.')


# Sidebar
st.sidebar.header('Input parameter')


with st.sidebar.form(key='my_form'):
	URL = st.text_input('Enter URL of YouTube video:')
	submit_button = st.form_submit_button(label='Get Text')


# Run custom functions if URL is entered 
if submit_button:
    get_yt(URL)
    transcribe_yt()
    
    

    with open("transcription.zip", "rb") as zip_download:
        btn = st.download_button(
            label="Download ZIP",
            data=zip_download,
            file_name="transcription.zip",
            mime="application/zip"
        )

with open('yt.txt') as f:
    text = f.read()

if st.checkbox("Summarize"):
    summarize(text)
    if st.checkbox("Translate to Hindi"):
        translate(text)



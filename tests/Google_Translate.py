import threading
from argostranslate import package, translate
from multiprocessing import shared_memory
import multiprocessing as mp
from scipy.io.wavfile import write
import speech_recognition as sr
from google.cloud import speech
import multiprocessing as mp
from ctypes import c_int8
import sounddevice as sd
import pyttsx3 as pytt
from os import getenv
import numpy as np
import keyboard
import queue
import gtts
import sys
import pyaudio
import wave
import time
import os
import io
import re

# https://www.one-tab.com/page/fE1FBnIoSiCp-JGVexmc9g
project_id = "gcloud_key.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=project_id
lang = "en-US"
#lang = "ja-JP"


client = speech.SpeechClient()
config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_automatic_punctuation=True,
        audio_channel_count=2,
        language_code=lang,
    )



def transcribe_audio(audio_queue):
    audio_buffer = b""
   
    try:
        audio_data = audio_queue.get(block=True,timeout=0.5)
        audio_buffer += audio_data
        if len(audio_buffer) >= 1024:
            client.content = audio_buffer
            #audio = speech.RecognitionAudio(content=audio)
            response = client.recognize(request={"config": config, "audio": client})
            for result in response.results:
                transcript = result.alternatives[0].transcript
                #conf = result.alternatives[0].confidence
                print(transcript)
                #return [transcript, conf]
            audio_buffer = b""
    except queue.Empty:
        print("Too many requests!!!")
        time.sleep(0.1)
    

    
def record_audio(shm_name,stop_flag,audio_queue):
   # Get a list of available input devices
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_id = []
    for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_id.append(i)
     
    #print(device_id)

    # Set up PyAudio stream
    chunk_size = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"
    
    stream = audio.open(format=format, 
                        channels=channels, 
                        rate=rate, 
                        input=True,
                        input_device_index=device_id[5], frames_per_buffer=chunk_size)

    # Continuously record and transcribe audio
    print("Recording audio!")
    while True:
        data = stream.read(chunk_size)
        audio_queue.put(data)
        if stop_flag.value == 1 or keyboard.is_pressed("q"):
            stop_flag.value = 1
            break
    stream.stop_stream()
    stream.close()
    audio.terminate()
    #shm_obj.close()
    print("Process : Exiting...")

def shm_block():
    np_arr = np.ndarray((44100,),dtype=np.uint16)
    shm = shared_memory.SharedMemory(create=True,size=np_arr.nbytes)
    shm_np_arr =np.ndarray(np_arr.shape,dtype=np.uint16,buffer=shm.buf)
    shm_np_arr[:] = np_arr[:]
    return shm, shm_np_arr

               
if __name__ == "__main__":
    audio_queue = mp.Queue()
    # Create a new process to run the getimg function
    stop_flag = mp.Value(c_int8, 0)
    shm_obj,shm_np_arr = shm_block()
    
    p = mp.Process(target=record_audio, args=(shm_obj.name,stop_flag,audio_queue))
    p.start()
    
    print("Starting program...")
    while True:
        text = transcribe_audio(audio_queue)
        #print(text)
        if keyboard.is_pressed("q") or stop_flag.value == 1:
            stop_flag.value = 1
            p.join()
            print("Main : Stopping!")
            sys.exit()
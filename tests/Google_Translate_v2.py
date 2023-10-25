import threading
from argostranslate import package, translate
from multiprocessing import shared_memory
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


project_id = "gcloud_key.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=project_id
lang = "en-US"
#lang = "ja-JP"

def transcribe_audio(audio):
    client = speech.SpeechClient()
    
    
    audio = speech.RecognitionAudio(content=audio)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_automatic_punctuation=True,
        audio_channel_count=2,
        language_code=lang,
    )

    try:
        response = client.recognize(request={"config": config, "audio": audio})
        for result in response.results:
            #print("Transcript: {}".format(result.alternatives[0].transcript))
            #print("Confidence: {}".format(result.alternatives[0].confidence))
            transcript = result.alternatives[0].transcript
            conf = result.alternatives[0].confidence
            #print("Full transcript: {}".format(result.alternatives))
            #print("len results:",len(result.alternatives))
            return [transcript, conf]
    except:
        print("Too many requests!!!")
    #print(response)
    

    
def record_audio(shm_name,stop_flag):
   # Get a list of available input devices
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_id = []
    for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                #print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))
                device_id.append(i)
     
    #print(device_id)

    # Set up PyAudio stream
    chunk_size = 2048
    format = pyaudio.paInt16
    channels = 1
    #rate = int(audio.get_device_info_by_index(device_id[5])['defaultSampleRate'])
    rate = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"
    
    stream = audio.open(format=format, 
                        channels=channels, 
                        rate=rate, 
                        input=True,
                        input_device_index=device_id[5], frames_per_buffer=chunk_size)

    shm_obj = shared_memory.SharedMemory(name=shm_name)
    shm_np_arr =np.ndarray((44100,),dtype=np.uint16, buffer=shm_obj.buf)

    # Continuously record and transcribe audio
    print("Recording audio!")
    #frames = []
    while True:
        data = stream.read(chunk_size)
        np_frame = np.frombuffer(data, dtype=np.int16)
        shm_np_arr[:len(np_frame)] = np_frame
        #print(shm_np_arr)
        #frames.append(data)
        #print(frames)
        time.sleep(0.3)
        if stop_flag.value == 1 or keyboard.is_pressed("q"):
            
            # stop recording
            #stream.stop_stream()
            #stream.close()
            #audio.terminate()
            #waveFile.close()
            #shm_obj.close()
            break
    # save the recorded audio to a file
    #waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    #waveFile.setnchannels(channels)
    #waveFile.setsampwidth(audio.get_sample_size(format))
    #waveFile.setframerate(rate)
    #waveFile.writeframes(b''.join(frames))
    stream.stop_stream()
    stream.close()
    audio.terminate()
    #waveFile.close()
    shm_obj.close()
    print("Process : Exiting...")

def shm_block():
    np_arr = np.ndarray((44100,),dtype=np.uint16)
    #print("shm",np_arr.shape)
    shm = shared_memory.SharedMemory(create=True,size=np_arr.nbytes)
    shm_np_arr =np.ndarray(np_arr.shape,dtype=np.uint16,buffer=shm.buf)
    shm_np_arr[:] = np_arr[:]
    return shm, shm_np_arr

def record_and_transcribe():
    # Set up Google Cloud client
    client = speech.SpeechClient()

    # Get a list of available input devices
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_id = []
    for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))
                device_id.append(i)
            
    #print(device_id)

    # Set up PyAudio stream
    chunk_size = 4096
    format = pyaudio.paInt16
    channels = 1
    #rate = int(audio.get_device_info_by_index(device_id[5])['defaultSampleRate'])
    rate = 16000
    stream = audio.open(format=format, channels=channels, rate=rate, input=True,
                        input_device_index=device_id[7], frames_per_buffer=chunk_size)

    # Continuously record and transcribe audio
    while True:
        frames = []
        for i in range(int(rate / chunk_size * 1)):  # Record for 2 seconds
            data = stream.read(chunk_size)
            frames.append(data)

        # Pass the recorded audio to the Speech-to-Text API and get the transcription
        audio_content = b''.join(frames)
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            enable_automatic_punctuation=True,
            sample_rate_hertz=rate,
            audio_channel_count=1,
            language_code=lang,
        )
        t1 = time.time()
        response = client.recognize(request={"config": config, "audio": audio})
        t2 = time.time()
        print("Elapsed time:", t2-t1)
        #print(response)
        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))
            #print("Confidence: {}".format(result.alternatives[0].confidence))
            text = result.alternatives[0].transcript
            #text = re.split(r'(?<=[.!?])\s+', text[0])
            print(text)
            #conf = result.alternatives[0].confidence
            #print("Full transcript: {}".format(result.alternatives))
            #print("len results:",len(result.alternatives))
        #return [transcript, conf]
    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()


               
if __name__ == "__main__":
    #record_audio()
    #record_and_transcribe()
    
    # Create a new process to run the getimg function
    stop_flag = mp.Value(c_int8, 0)
    shm_obj,shm_np_arr = shm_block()
    
    #t1 = threading.Thread(target=stop_program,args=(stop_flag,))
    #t1.start()
    
    p = mp.Process(target=record_audio, args=(shm_obj.name,stop_flag))
    p.start()
    
    print("Starting program...")
    while True:
        audio_data = shm_np_arr.tobytes()
        text = transcribe_audio(audio_data)
        print(text)
        #print(stop_flag.value)
        #print(shm_np_arr)
        if keyboard.is_pressed("q"):
            stop_flag.value = 1
            p.join()
            print("Main : Stopping!")
            sys.exit()
        time.sleep(0.3)
    #file = "test.wav"
    #file = "jap.wav"
    #t1 = time.time()
    #text = transcribe_audio(file)
    #t2 = time.time()
    #print("Elapsed time:", t2-t1)
    
    #print(text[0],text[1],"\n")
    #engine = pytt.init()
    #rate = engine.getProperty('rate')  
    #engine.setProperty('rate', 200)
    #volume = engine.getProperty('volume')
    #engine.setProperty('volume',100.0)
    #voices = engine.getProperty('voices')
    #for voice in voices:
    #    print("Voice: %s" % voice.name)
    #    print(" - ID: %s" % voice.id)
    #    print(" - Languages: %s" % voice.languages)
    #    print(" - Gender: %s" % voice.gender)
    #    print(" - Age: %s" % voice.age)
    #    print("\n")
    #engine.setProperty("voice",voices[2].id)
    
    
    """
    from_code = "ja"
    to_code = "en"
    text = re.split(r'(?<=[.!?])\s+', text[0])
        
    
    package.install_from_path('ja_en.argosmodel')
    installed_languages = translate.get_installed_languages()
    print([str(lang) for lang in installed_languages])
    #translator = ja.get_translation(en)
    trans = installed_languages[1].get_translation(installed_languages[0])
    for i in text: 
        print(i)
        test = trans.translate("ここから出て行け！あなたはとても愚かです。ええ、そうです。")
        print(test)
        #translatedText = translator.translate(i)
    """
        
        
        
    #argostranslate.package.update_package_index()
    #print(get_installed_languages()) # [LanguageModel_English, LanguageModel_Spanish]
    #translator = es.get_translation(en)
    #    engine.say(i)
    #    engine.runAndWait()
    #engine.stop()
    
    
    
    #print("\n")
    #text2 = transcribe_sr(file)
    #print(text)
    
    
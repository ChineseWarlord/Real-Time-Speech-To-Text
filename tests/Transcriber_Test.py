# Import basic libraries and initiate functions
from faster_whisper import WhisperModel
from numba import njit,cuda
from typing import Union
import numpy as np
import animation
import threading
import keyboard
import pyaudio
import whisper
import psutil
import queue
import wave
import time
import sys

def get_models(models):
    #print("Available models:")
    list = []
    for i, model in enumerate(models):
        #print(f"{i}: {model}")
        list.append(model)
    return list
  
def run_model(type:str,models:str,workers:int):
    if type == "openai":
        model = whisper.load_model(models)
    elif type == "ctranslate":
        model = WhisperModel(models,device="cuda",compute_type="int8_float16",num_workers=workers)
    
    return model
            
def transcribe_fast(model,file: Union[str,np.ndarray],size:int,y:bool,print_out:bool):
    model = model
    
    # convert audio data buffer to a NumPy ndarray
    #audio_array = np.frombuffer(file, dtype=np.int16)
    
    # Return segments and info such as detected lang. and prob.
    segments, info = model.transcribe(audio=file,beam_size=size,word_timestamps=y)
    text = segments
    if print_out == True:
        print("\nDetected language '%s' with probability %f" % (info.language, info.language_probability), end="")

    # Print out segments
    if print_out == True:
        for segment in segments:
            print("\n[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text), end="")
            
    return segments
  
def record_audio(audio_obj,mic_id):
    # Recording parameters
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    rec_sec = 10
    stream = audio_obj.open(format=format, 
                        channels=channels, 
                        rate=rate, 
                        input=True,
                        input_device_index=mic_id,
                        frames_per_buffer=chunk)
    print("Recording!")
    while 1:
        # create new WAV file
        filename = "output.wav"
        wf = wave.open(filename, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(audio_obj.get_sample_size(format))
        wf.setframerate(rate)
        
        for i in range(0,int(rate / chunk * rec_sec)):
            data = stream.read(chunk)
            #data = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
            
            #audio_data = np.frombuffer(data,dtype=np.int16).flatten().astype(np.float32) / 32768.0
            #audio_buffer.put(audio_data)
            try:
                wf.writeframes(data)
            except:
                print("Record : Too many requests!")
            #audio_data = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0 
            #audio_data = np.frombuffer(data, dtype=np.int16)
            #audio_data = audio_data / 32768.0  # convert to float
            #audio_data = np.frombuffer(data, dtype=np.int16, count=len(data)//2, offset=0)
            #audio_data = audio_data.astype(np.float32, order='C') / 32768.0
            #audio_buffer.put(audio_data)
        wf.close()
        time.sleep(0.02)
        if keyboard.is_pressed("w"):
            # stop recording
            stream.stop_stream()
            stream.close()
            audio_obj.terminate()
            break
    
    print("Closing thread...")
    sys.exit()
    
    
# Get a list of available input devices
audio_obj= pyaudio.PyAudio()
info = audio_obj.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
device_id = []
for i in range(0, numdevices):
    if (audio_obj.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", audio_obj.get_device_info_by_host_api_device_index(0, i).get('name'))
        device_id.append(i)


# Initialize audio buffer
audio_buffer = queue.Queue()

# Create audio recording thread
t1 = threading.Thread(target=record_audio, args=(audio_obj,device_id[2]))
t1.start()

# Check for available models, then download the preferred.
models = whisper.available_models()
id = get_models(models)

model = run_model("ctranslate","medium",4)

# Transcribe audio
print("Transcribing!")
while 1:
    #audio_data = audio_buffer.get()
    #audio_data = audio_data.astype(np.float32)
    audio_data = "output.wav"
    #t1 = time.time()
    #text = transcribe_fast(model,audio_data,5,True,True)
    #audio_data = audio_buffer.get()
    #audio_data = np.frombuffer(audio_data, np.int16)
    prev_segment = ""
    try: 
        segments, info = model.transcribe(audio=audio_data,beam_size=5,word_timestamps=False,vad_filter=True,task="translate")
        
       
        
        # Print out segments
        for segment in segments:
            #test = segment.text
            #print(test)
            print("\n'%s' %.2f" % (info.language, info.language_probability),)
            print(segment.text)
        #text = segments.text
        #print(f"TEXT: {text}\n")
        #t2 = time.time()
        #print("\nElapsed time:", t2-t1, end="")
    except:
        print("Transcribe : Too many requests!")
    if keyboard.is_pressed("q"):
            print("\nStopping...")
            sys.exit()
            break


# Calculate memory usage
pid = psutil.Process()
memory_info = pid.memory_info()
print("Memory usage:", memory_info.rss / 1024 / 1024, "MB")



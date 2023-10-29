# Import basic libraries
import keyboard
import pyaudio
import queue
import wave
import sys


  
def record_audio(audio_obj,mic_id,STOP):
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
            wf.close()
            #audio_data = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0 
            #audio_data = np.frombuffer(data, dtype=np.int16)
            #audio_data = audio_data / 32768.0  # convert to float
            #audio_data = np.frombuffer(data, dtype=np.int16, count=len(data)//2, offset=0)
            #audio_data = audio_data.astype(np.float32, order='C') / 32768.0
            #audio_buffer.put(audio_data)
        
        
            if keyboard.is_pressed("w") or STOP == True:
                # stop recording
                stream.stop_stream()
                stream.close()
                audio_obj.terminate()
                break
            if STOP == True:
                break
    
    print("Closing thread...")
    sys.exit()
    
if __name__ == "__main__":   
    # Get a list of available input devices
    audio_obj= pyaudio.PyAudio()
    info = audio_obj.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_id = []
    for i in range(0, numdevices):
        if (audio_obj.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio_obj.get_device_info_by_host_api_device_index(0, i).get('name'))
            device_id.append(i)
            
    device = int(input("Choose device ID: "))
    
    # Initialize audio buffer
    audio_buffer = queue.Queue()
    STOP = False
    # Create audio recording thread
    #t1 = threading.Thread(target=record_audio, args=(audio_obj,device_id[2],STOP))
    #t1.start()

    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    rec_sec = 10
    stream = audio_obj.open(format=format, 
                        channels=channels, 
                        rate=rate, 
                        input=True,
                        input_device_index=device,
                        frames_per_buffer=chunk)

    print("Recording!")
    #time.sleep(5)
    #exit()
    count = 1
    # create new WAV file
    filename = "output.wav"
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(audio_obj.get_sample_size(format))
    wf.setframerate(rate)
    while 1:
       
        
        for i in range(0,int(rate / chunk * rec_sec+1)):
            data = stream.read(chunk)
        #data = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
        
        #audio_data = np.frombuffer(data,dtype=np.int16).flatten().astype(np.float32) / 32768.0
        #audio_buffer.put(audio_data)
        
            wf.writeframes(data)
            if keyboard.is_pressed("esc") or STOP == True:
                # stop recording
                stream.stop_stream()
                audio_obj.terminate()
                stream.close()
                break
        break
            
        
            
    wf.close()
    sys.exit("Closing program...")
    print(f"Writing to file: {count}")
    count += 1
        
            #audio_data = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0 
            #audio_data = np.frombuffer(data, dtype=np.int16)
            #audio_data = audio_data / 32768.0  # convert to float
            #audio_data = np.frombuffer(data, dtype=np.int16, count=len(data)//2, offset=0)
            #audio_data = audio_data.astype(np.float32, order='C') / 32768.0
            #audio_buffer.put(audio_data)
        
        
       

    ## Calculate memory usage
    #pid = psutil.Process()
    #memory_info = pid.memory_info()
    #print("Memory usage:", memory_info.rss / 1024 / 1024, "MB")



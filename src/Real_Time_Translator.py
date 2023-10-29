from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from deep_translator import GoogleTranslator
from queue import Queue

import speech_recognition as sr
import translators as ts
import threading
import keyboard
import whisper
import pyaudio
import queue
import time
import sys
import io
import os

from utils import recording_utils, model_utils, subtitles_utils

def record_audio(data_queue):
    # Parameters used to check audio energy level to start/stop recording
    energy_threshold = int(150)
    record_timeout = float(0.75)
    
    # Initialize the recognizer object
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold # Used as a sensitivity checker
    recorder.dynamic_energy_threshold = False # Can be used instead of a manual energy threshold
    
    # Retrieve audio devices and setup microphone object
    input_devices = recording_utils.get_devices(input_output="input")
    device_id = int(input("\nChoose input device: "))
    source = sr.Microphone(sample_rate=44100, device_index=input_devices[device_id])

    
    with source:
        recorder.adjust_for_ambient_noise(source) # Automatically adjust microphone to reduce background noise

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread queue
        data = audio.get_raw_data()
        data_queue.put(data)
        if keyboard.is_pressed("esc"):
            print("\n\nExiting Recorder Thread")
            sys.exit()

    # Create a background thread that will pass the raw audio bytes
    recorder.listen_in_background(
        source, record_callback, phrase_time_limit=record_timeout
    )
    
    return source
    
def transcribe_audio(data_queue, source):
    # Parameters used to determine when a phrase is done
    phrase_timeout = float(1)
    phrase_time = None
    last_sample = bytes()
    
    # Create temporary file to store raw audio data and empty transcript list
    temp_file = NamedTemporaryFile().name
    transcript = [""]
    
    # Choose model to run
    models = whisper.available_models()
    id = model_utils.get_models(models)
    model = model_utils.run_model("ctranslate", id[int(input("\nChoose model: "))], 4,"cuda", "float16")
    #ts.preaccelerate_and_speedtest()
    
    # Initialize subtitle thread and queue
    q = queue.Queue()
    stop_event = threading.Event()
    subtitle_thread = threading.Thread(target=subtitles_utils.show_subtitle,args=(100, 100, q, stop_event),daemon=True)
    subtitle_thread.start()
    
    # Clear terminal
    os.system("cls" if os.name == "nt" else "clear")
    print("Ready to transcribe\n")
    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue
            if not data_queue.empty():
                phrase_complete = False
                
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(
                    seconds=phrase_timeout
                ):
                    last_sample = bytes()
                    phrase_complete = True
                    
                # Mark the last time we received new audio data from the queue
                phrase_time = now

                # Concatenate current audio data with the latest audio data in queue
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data
                audio_data = sr.AudioData(
                    last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH
                )
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes
                with open(temp_file, "w+b") as f:
                    f.write(wav_data.read())

                # Read the transcription.
                segments, _ = model.transcribe(
                    audio=temp_file,
                    beam_size=5,
                    word_timestamps=False,
                    task="transcribe",
                    vad_filter=True,
                    #vad_parameters=dict(min_silence_duration_ms=1000)
                )

                # If we detected a pause between recordings, add a new item to our transcripion.
                # Otherwise edit the existing one.
                # print("\nDetected language '%s' with probability %f" % (info.language, info.language_probability))
                if phrase_complete:
                    # Print out segments
                    for segment in segments:
                        transcript.append(segment.text)
                else:
                    try:
                        for segment in segments:
                            transcript[-1] = segment.text
                    except Exception as e:
                        print(f"Error: {e}")

                # Clear terminal to reprint the updated transcription
                #os.system("cls" if os.name == "nt" else "clear")
                for line in transcript:
                    trans = GoogleTranslator("ja","en").translate(line)
                    #trans = ts.translate_text(line,translator="google",from_language="auto",to_language="en")
                    #trans = GoogleTranslator("ja","en").translate_batch(transcript)
                    #print("Transcript:", line)
                    print("Transcript:", trans)
                    q.put(trans)
                transcript.clear()
                #trans.clear()
                #print(transcript)
                
                # Flush stdout to display text in real-time
                #print("", end="", flush=True)
                if keyboard.is_pressed("esc"):
                    print("\n\nExiting!")
                    stop_event.set()
                    subtitle_thread.join()
                    sys.exit()

                # Infinite loops are bad for processors, must sleep.
                #time.sleep(0.05)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt")
            print("Exiting!")
            break



if __name__ == "__main__":
    # Audio parameters
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    rec_sec = 10

    # Initialize audio queue, audio recording and transcription
    data_queue = Queue()
    source = record_audio(data_queue)
    transcribe_audio(data_queue, source)
    
    
    """
    models = whisper.available_models()
    id = get_models(models)
    model = run_model("ctranslate",id[int(input("\nChoose model: "))],4)
    
    t1 = time.time()
    #text = transcribe_fast(model,file,5,True,True)
    segments, info = model.transcribe(audio=data,beam_size=5,word_timestamps=True,task="transcribe")
    print("\nDetected language '%s' with probability %f" % (info.language, info.language_probability))

    # Print out segments
    list = []
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        list.append(segment.text)
        #print(f"items in list: {list}")
    t2 = time.time()
    print("\n\nElapsed time:", t2-t1)
    
    print(list)
    """

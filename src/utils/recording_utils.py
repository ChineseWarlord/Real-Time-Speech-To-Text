import numpy as np
import pyaudio
import wave

def get_devices(input_output="input"):
    audio_obj = pyaudio.PyAudio()
    num_devices = audio_obj.get_host_api_info_by_index(0).get("deviceCount")
    device_input_id = []
    device_output_id = []

    for i in range(0, num_devices):
        if input_output == "input":
            if audio_obj.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels") > 0:
                device = audio_obj.get_device_info_by_host_api_device_index(0, i).get("name")
                print(f"Input Device ID: {i} | {device}")
                device_input_id.append(i)
                
        elif input_output == "output":
            if audio_obj.get_device_info_by_host_api_device_index(0, i).get("maxOutputChannels") > 0:
                device = audio_obj.get_device_info_by_host_api_device_index(0, i).get("name")
                print(f"Input Device ID: {i} | {device}")
                device_output_id.append(i)
                
    return device_input_id



def record_audio(channels, rate, chunk, rec_sec):
    p = pyaudio.PyAudio()
    input_device_ids = get_devices(input_output="input")
    input_device_id = int(input("\nChoose input device: "))

    stream = p.open(
        format=format,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=input_device_ids[input_device_id],
        frames_per_buffer=chunk,
    )

    print("Recording!")
    np_data = np.array([], dtype=np.int16)
    for i in range(0, int(rate / chunk * rec_sec + 1)):
        data = stream.read(chunk)
        np_data_chunk = np.frombuffer(data, dtype=np.int16)
        np_data = np.concatenate((np_data, np_data_chunk))

    stream.stop_stream()
    stream.close()

    """
    Play back the recorded audio on the selected output device
    output_device_ids = get_devices(input_output='output')
    output_device_id = int(input("\nChoose output device: "))
    print("Playing!")
    stream_out = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        output=True,
                        output_device_index=output_device_ids[output_device_id],
                        frames_per_buffer=chunk)
    stream_out.write(np_data.tobytes())
    stream_out.stop_stream()
    stream_out.close()
    """
    
    p.terminate()

    wf = wave.open("test_audio.wav", "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(np_data.tobytes())
    wf.close()

    return np_data
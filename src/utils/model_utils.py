from faster_whisper import WhisperModel
import whisper

def get_models(models):
    print("\nAvailable models:")
    list = []
    for i, model in enumerate(models):
        print(f"{i}: {model}")
        list.append(model)
    return list

def run_model(type: str, models: str, workers: int, device:str, compute_type:str):
    if type == "openai":
        try:
            model = whisper.load_model(models)
            return model
        except:
            print("Error occured!")
    elif type == "ctranslate":
        try:
            model = WhisperModel(models,device=device,compute_type=compute_type,num_workers=workers, download_root="../models/") # GPU ONLY
            #model = WhisperModel(models,device=device,num_workers=workers, download_root="../models/") # CPU ONLY
            return model
        except:
            print("Error occured!")
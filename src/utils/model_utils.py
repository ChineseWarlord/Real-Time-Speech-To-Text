from faster_whisper import WhisperModel
import whisper

def get_models(models):
    print("\nAvailable models:")
    list = []
    for i, model in enumerate(models):
        print(f"{i}: {model}")
        list.append(model)
    return list

def run_model(type: str, models: str, workers: int):
    if type == "openai":
        try:
            model = whisper.load_model(models)
            return model
        except:
            print("Error occured!")
    elif type == "ctranslate":
        try:
            model = WhisperModel(
                models, device="cuda", compute_type="int8_float16", num_workers=workers
            )
            return model
        except:
            print("Error occured!")
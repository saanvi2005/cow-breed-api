from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import speech_recognition as sr
from pydub import AudioSegment

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ✅ Ensure audio directory exists
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ✅ Serve static files for TTS audio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

def generate_tts(text, language):
    filename = f"output_{hash(text)}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    tts = gTTS(text=text, lang=language)
    tts.save(filepath)
    return filename

# ✅ Expanded cow breed data
cow_data = {
    "gir": {"origin": "Gujarat", "milk_yield": "10-15 liters per day", "features": "It has a high milk yield and is resistant to heat."},
    "sahiwal": {"origin": "Punjab", "milk_yield": "8-12 liters per day", "features": "This breed is known for its drought resistance and disease resistance."},
    "red sindhi": {"origin": "Sindh", "milk_yield": "10-12 liters per day", "features": "It adapts well to hot climates and has good fertility."},
    "tharparkar": {"origin": "Rajasthan", "milk_yield": "10-14 liters per day", "features": "This breed is a good milker and is both heat and drought resistant."},
    "ongole": {"origin": "Andhra Pradesh", "milk_yield": "8-12 liters per day", "features": "It has a strong build and is resistant to diseases."},
}

class QueryRequest(BaseModel):
    question: str
    language: str

@app.post("/ask")
def ask_question(data: QueryRequest):
    question = data.question.lower()
    language = data.language.lower()

    breeds_mentioned = [breed for breed in cow_data.keys() if breed in question]

    if len(breeds_mentioned) > 1:
        return compare_cows(data)

    answer = None
    for breed, details in cow_data.items():
        if breed in question:
            answer = (f"The {breed.capitalize()} breed originates from {details['origin']}. "
                      f"It produces around {details['milk_yield']}. "
                      f"{details['features']}")
            break

    if not answer:
        answer = "Sorry, I don't have information on that breed."

    try:
        translated_answer = GoogleTranslator(source='en', target=language).translate(answer)
    except Exception:
        translated_answer = answer

    audio_file = generate_tts(translated_answer, language)
    base_url = "https://cow-breed-api.onrender.com"

    return {"response": translated_answer, "audio_url": f"{base_url}/audio/{audio_file}"}

@app.post("/compare")
def compare_cows(data: QueryRequest):
    question = data.question.lower()
    language = data.language.lower()

    breeds = [breed for breed in cow_data.keys() if breed in question]

    if len(breeds) < 2:
        return {"response": "Please mention at least two breeds for comparison."}

    comparison_result = "Here's a comparison of the mentioned breeds:\n\n"
    for breed in breeds:
        details = cow_data[breed]
        comparison_result += (f"The {breed.capitalize()} breed originates from {details['origin']}. "
                              f"It produces around {details['milk_yield']}. "
                              f"{details['features']}\n\n")

    try:
        translated_answer = GoogleTranslator(source='en', target=language).translate(comparison_result)
    except Exception:
        translated_answer = comparison_result

    audio_file = generate_tts(translated_answer, language)
    base_url = "https://cow-breed-api.onrender.com"

    return {"response": translated_answer, "audio_url": f"{base_url}/audio/{audio_file}"}

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...), language: str = "en"):
    try:
        temp_audio_path = f"temp_{file.filename}"
        with open(temp_audio_path, "wb") as f:
            f.write(file.file.read())

        audio = AudioSegment.from_file(temp_audio_path)
        wav_path = temp_audio_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        # Set language for recognition
        lang_code = "hi-IN" if language.lower() == "hi" else "en-US"
        text = recognizer.recognize_google(audio_data, language=lang_code)

        os.remove(temp_audio_path)
        os.remove(wav_path)

        return {"transcription": text}
    except Exception as e:
        return {"error": f"Speech recognition failed: {str(e)}"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

app = FastAPI()

# ✅ Enable CORS (Fix frontend issues)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def generate_tts(text, language):
    filename = "output.mp3"
    tts = gTTS(text=text, lang=language)
    tts.save(filename)
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

    # ✅ Detect comparison questions
    comparison_keywords = ["compare", "difference between", "vs", "versus"]
    breeds_mentioned = [breed for breed in cow_data.keys() if breed in question]

    if any(keyword in question for keyword in comparison_keywords) or len(breeds_mentioned) > 1:
        return compare_cows(data)  # ✅ Call compare function if it's a comparison question

    answer = None
    for breed, details in cow_data.items():
        if breed in question:
            answer = (f"The {breed.capitalize()} breed originates from {details['origin']}. "
                      f"It produces around {details['milk_yield']}. "
                      f"{details['features']}")
            break

    if not answer:
        return {"response": "Sorry, I don't have information on that breed."}

    # ✅ Properly handle translation errors
    try:
        translated_answer = GoogleTranslator(source='en', target=language).translate(answer)
    except Exception as e:
        translated_answer = answer  # Fallback to English

    return {"response": translated_answer}

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

    # ✅ Properly handle translation errors
    try:
        translated_answer = GoogleTranslator(source='en', target=language).translate(comparison_result)
    except Exception as e:
        translated_answer = comparison_result  # Fallback to English

    return {"response": translated_answer}

@app.post("/text-to-speech")
def text_to_speech(data: QueryRequest):
    text = data.question  
    language = data.language.lower()
    
    audio_file = generate_tts(text, language)
    
    base_url = "https://cow-breed-api.onrender.com"
    return {"audio_url": f"{base_url}/{audio_file}"}

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)


import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import time
import threading
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

import numpy as np
import faiss
from jose import jwt
from jose.exceptions import JWTError
from fastapi import (
    FastAPI, Depends, HTTPException, BackgroundTasks,
    UploadFile, File
)
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from serpapi import GoogleSearch
from googletrans import Translator
from gtts import gTTS

# === Face Recognition Module (if implemented separately) ===
from face_recognition_module import recognize_and_greet

# === FastAPI setup ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))

# === Authentication ===
fake_users_db = {"robot": {"username": "robot", "password": "secret123"}}
SECRET_KEY = "234219080983847398479VDJBJDBBOOSIOJ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6000
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_request(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user["username"]})
    print(f"[Backend] Generated token: {token}")
    return {"access_token": token, "token_type": "bearer"}

# === Models ===
class Command(BaseModel):
    action: str
    language_code: str 

class ReminderRequest(BaseModel):
    task: str
    time: str

class GoogleQuery(BaseModel): 
    query: str

class TextRequest(BaseModel):
    text: str

class TranslationRequest(BaseModel):
    text: str
    source_lang: Optional[str] = "auto"
    target_lang: str = "en"

# === State ===
current_command = {"action": "Ready"}

# @app.post("/command")
# async def set_command(cmd: Command, user=Depends(authenticate_request)):
#     print(f"[Backend] Received command: {cmd.action}")
#     current_command["action"] = cmd.action
#     return {"message": f"Command set: {cmd.action}"}

@app.post("/command")
async def set_command(cmd: Command, user=Depends(authenticate_request)):
    print(f"[Backend] Received command: {cmd.action} ({cmd.language_code})")
    current_command["action"] = {
        "text": cmd.action,
        "language_code": cmd.language_code
    }
    return {"message": f"Command set: {cmd.action}"}




@app.get("/command")
def get_command(user=Depends(authenticate_request)):
    action = current_command["action"]
    print(f"[Backend] Returning command: {action}")
    current_command["action"] = ""
    return {"action": action}

# === Google Query ===
@app.post("/google-query")
async def google_query(query: GoogleQuery, user=Depends(authenticate_request)):
    q = query.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query")

    params = {
        "engine": "duckduckgo",
        "q": q,
        "kl": "us-en",
        "api_key": "0e8fcd6d33d7ae27269dda3ae568c927289141a884b4cc5d433adeb71f013a3b"
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if "answer" in results:
            answer_text = results["answer"]
        elif "answer_box" in results:
            answer_text = results["answer_box"].get("answer", "")
        elif results.get("organic_results"):
            answer_text = results["organic_results"][0].get("snippet", "")
        else:
            answer_text = "Sorry, I couldn't find a good answer."
    except Exception as e:
        print(f"[Backend] DuckDuckGo error: {e}")
        answer_text = "Sorry, there was an error retrieving the answer."

    current_command["action"] = answer_text
    print(f"[Backend] Robot will say: {answer_text}")
    return {"message": answer_text}

# === Reminders ===
def schedule_reminder(task: str, run_at: datetime):
    wait = (run_at - datetime.now()).total_seconds()
    if wait > 0:
        time.sleep(wait)
    current_command["action"] = f"Reminder: {task}"
    print(f"[Reminder] Triggered: {task}")

@app.post("/remind-me")
async def remind_me(request: ReminderRequest, background_tasks: BackgroundTasks, user=Depends(authenticate_request)):
    now = datetime.now()
    t = request.time.strip()
    try:
        dt = datetime.strptime(t, "%H:%M")
    except ValueError:
        try:
            dt = datetime.strptime(t, "%I:%M %p")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format")

    run_at = now.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
    if run_at < now:
        run_at += timedelta(days=1)

    background_tasks.add_task(schedule_reminder, request.task, run_at)
    return {"message": f"Reminder set for '{request.task}' at {run_at.strftime('%I:%M %p')}"}

# === Face Recognition ===
from fastapi import UploadFile, File
import shutil
import os

@app.post("/add-face/")
def add_face(name: str, file: UploadFile = File(...)):
    # Define absolute path to save uploaded face image
    save_dir = "/Users/hassanchaudhry/Desktop/Ami/known_faces"
    os.makedirs(save_dir, exist_ok=True)  # ensure the directory exists
    file_location = os.path.join(save_dir, f"{name}.jpg")
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"message": f"{name} added successfully!", "saved_to": file_location}
 
@app.post("/start-face-recognition")
def start_face_recognition():
    threading.Thread(target=recognize_and_greet, args=(current_command,), daemon=True).start()
    return {"message": "Face recognition started."} 



# === Fun Facts ===
FACTS = [
    "Honey never spoils.",
    "Octopuses have three hearts.",
    "Bananas are berries, but strawberries are not.",
    "A group of flamingos is called a 'flamboyance'.",
    "There are more stars in the universe than grains of sand on Earth."
]

@app.get("/fact")
def random_fact():
    fact = random.choice(FACTS)
    current_command["action"] = f"Did you know that, {fact}"
    return {"fact": fact}

# === Translation + TTS ===
import os
import uuid
from gtts import gTTS
from fastapi import BackgroundTasks, HTTPException, Depends, APIRouter
from googletrans import Translator
from pydantic import BaseModel

# Setup
import os
import uuid
from fastapi import BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from googletrans import Translator
from gtts import gTTS

AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
translator = Translator()

DEFAULT_VOICES = {
    "eng": {"name": "Amy", "backend": "aws_polly_neural_v1"},
    "fra": {"name": "Lea", "backend": "aws_polly_neural_v1"},
    "deu": {"name": "Vicki", "backend": "aws_polly_neural_v1"},
    "hin": {"name": "Kajal", "backend": "aws_polly_neural_v1"},
    "pol": {"name": "Ola", "backend": "aws_polly_neural_v1"},
    "spa": {"name": "Lupe", "backend": "aws_polly_neural_v1"},
    "ita": {"name": "Bianca", "backend": "aws_polly_neural_v1"},
    "por": {"name": "Vitoria", "backend": "aws_polly_neural_v1"},
    "jpn": {"name": "Mizuki", "backend": "aws_polly_neural_v1"},
    "ara": {"name": "Zeina", "backend": "aws_polly_neural_v1"},
}

# Map ISO 639-1 (googletrans/gTTS) codes to your voice language codes
LANG_CODE_MAP = {
    "en": "eng",
    "fr": "fra",
    "de": "deu",
    "hi": "hin",
    "pl": "pol",
    "es": "spa",
    "it": "ita",
    "pt": "por",
    "ja": "jpn",
    "ar": "ara",
}

current_command = {"action": ""}  # your global command dict

def cleanup_audio_files():
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith(".mp3"):
            filepath = os.path.join(AUDIO_DIR, filename)
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Failed to delete {filepath}: {e}")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

@app.post("/translate")
async def translate_text(
    request: TranslationRequest,
    background_tasks: BackgroundTasks,
    user=Depends(authenticate_request)
):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text to translate is empty")

    try:
        # Translate text
        result = translator.translate(request.text, src=request.source_lang, dest=request.target_lang)
        translated_text = result.text

        # Clean old audio files in background
        background_tasks.add_task(cleanup_audio_files)

        # Generate audio filename and path
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Generate TTS audio for translated text
        gTTS(text=translated_text, lang=request.target_lang).save(filepath)

        # Map lang code for your voice dict
        voice_lang_code = LANG_CODE_MAP.get(request.target_lang, "eng")

        # Set robot command with text and mapped language_code for correct voice
        current_command["action"] = {
            "text": translated_text,
            "language_code": voice_lang_code
        }

        return {
            "message": translated_text,
            "audio_url": f"/static/audio/{filename}",
            "robot_command": current_command["action"]
        }

    except Exception as e:
        print(f"Translation or TTS failed: {e}")
        raise HTTPException(status_code=500, detail="Translation or audio generation failed")



# === RAG Document Upload ===

# === FAISS Setup ===
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from transformers import pipeline
import pyttsx3
import asyncio

# Dummy auth
def authenticate_request():
    return True


document_store = []  # Stores dicts of uploaded docs
current_command = {"action": ""}  # Global state for robot command

# Load QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=-1)

# Init text-to-speech engine
tts_engine = pyttsx3.init()

def speak_text(text: str): 
    def run_tts():
        tts_engine.say(text)
        tts_engine.runAndWait()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_tts)

class RAGQuery(BaseModel):
    question: str
    top_k: Optional[int] = 3  # unused but kept for structure

@app.post("/upload-docs/")
async def upload_docs(files: List[UploadFile] = File(...), user=Depends(authenticate_request)):
    for file in files:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        document_store.append({"text": text, "source": file.filename})
    return {"message": f"{len(files)} files processed and stored."}

@app.post("/qa/")
async def question_answering(request: RAGQuery, user=Depends(authenticate_request)):
    if not document_store:
        raise HTTPException(status_code=400, detail="No documents uploaded.")

    context = " ".join([doc["text"] for doc in document_store])
    result = qa_pipeline(question=request.question, context=context)

    answer_text = result["answer"]
    current_command["action"] = answer_text
    print(f"[Backend] Robot will say: {answer_text}")
    speak_text(answer_text)

    return {
        "question": request.question,
        "answer": answer_text,
        "score": result["score"]
    }

from fastapi import FastAPI, Query
import httpx


TOMTOM_API_KEY = "5MDz8YWK3tiDPUbpMyssgFKyHPc3ujlE"

def format_time(seconds: int) -> str:
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"

def suggest_transport(distance_meters: int, travel_time_seconds: int) -> str:
    km = distance_meters / 1000
    if km < 1:
        return "Walking is recommended — it's very close!"
    elif km < 5:
        return "You could walk or cycle. Car is also an option."
    elif km < 15:
        return "Consider cycling or using public transport."
    else:
        return "Driving or public transport is best due to distance."

@app.get("/simple-journey")
async def simple_journey(
    start_postcode: str = Query(...),
    end_postcode: str = Query(...)
):
    async with httpx.AsyncClient() as client:
        # Get coordinates
        start_resp = await client.get(f"https://api.postcodes.io/postcodes/{start_postcode}")
        if start_resp.status_code != 200:
            return {"error": "Invalid start postcode"}
        start = start_resp.json()["result"]
        start_coords = f"{start['latitude']},{start['longitude']}"

        end_resp = await client.get(f"https://api.postcodes.io/postcodes/{end_postcode}")
        if end_resp.status_code != 200:
            return {"error": "Invalid end postcode"}
        end = end_resp.json()["result"]
        end_coords = f"{end['latitude']},{end['longitude']}"

        # TomTom route call
        url = (
            f"https://api.tomtom.com/routing/1/calculateRoute/"
            f"{start_coords}:{end_coords}/json"
            f"?key={TOMTOM_API_KEY}&travelMode=car&traffic=true"
        )
        route_resp = await client.get(url)
        if route_resp.status_code != 200:
            return {"error": "TomTom API request failed"}

        data = route_resp.json()
        summary = data["routes"][0]["summary"]

        distance_meters = summary["lengthInMeters"]
        travel_time_seconds = summary["travelTimeInSeconds"]
        delay_seconds = summary.get("trafficDelayInSeconds", 0) 

        recommendation = suggest_transport(distance_meters, travel_time_seconds)

        return {
            "distance_km": round(distance_meters / 1000, 2),
            "estimated_travel_time": format_time(travel_time_seconds),
            "traffic_delay": format_time(delay_seconds),
            "recommendation": recommendation,
            "tip": "This is based on car route. For public transport, try /journey with TransportAPI."
        }

from fastapi import FastAPI, Query
import httpx


TRANSPORT_API_APP_ID = "f9ea4032"
TRANSPORT_API_APP_KEY = "6a0860f022d8d857bd4c25c23c2670f8"

# Helper to geocode a postcode
async def geocode_postcode(postcode: str) -> tuple:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.postcodes.io/postcodes/{postcode}")
        if resp.status_code != 200:
            return None
        result = resp.json()["result"]
        return result["latitude"], result["longitude"]


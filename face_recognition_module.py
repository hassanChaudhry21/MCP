import os
import cv2
import pickle
import face_recognition
import pyttsx3
import datetime
import random
import json
from deepface import DeepFace


# Paths
KNOWN_FACES_DIR = "/Users/hassanchaudhry/Desktop/Ami/known_faces"
ENCODING_FILE = "/Users/hassanchaudhry/Desktop/Ami/face_encodings.pkl"
MEMORY_FILE = "visit_log.json"
UNKNOWN_DIR = "unknown_faces"  # Optional: to store unknown faces

# Config
SAVE_UNKNOWN = True
FRAME_SKIP = 2
RECOGNITION_THRESHOLD = 0.5  # Lower = stricter

JOKES = [
    "Why did the computer go to the doctor? It had a virus!",
    "I'm not lazy, I'm on energy-saving mode.",
    "Why did the robot cross the road? Because it was programmed by a chicken!",
    "Beep boop! I'm smarter than I look.",
    "Never trust atoms. They make up everything."
]

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def load_encodings(encoding_file):
    with open(encoding_file, 'rb') as f:
        return pickle.load(f)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def greet_user(name, memory, current_command, mood=None): 
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_seen = memory.get(name)

    if last_seen:
        message = f"Welcome back, {name}! Last time I saw you was on {last_seen}."
    else:
        message = f"Hello, {name}! Nice to meet you."

    mood_msg = f" You seem to be feeling {mood.lower()} today." if mood else ""
    joke = random.choice(JOKES)
    full_message = f"{message}{mood_msg} {joke}"

    speak(full_message)
    current_command["action"] = full_message
    memory[name] = now
    save_memory(memory)


def save_unknown_face(frame):
    if not os.path.exists(UNKNOWN_DIR):
        os.makedirs(UNKNOWN_DIR)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{UNKNOWN_DIR}/unknown_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"[Saved unknown face at] {filename}")

def recognize_and_greet(current_command):
    known_encodings, known_names = load_encodings(ENCODING_FILE)
    memory = load_memory()
    greeted_names = set()

    video_capture = cv2.VideoCapture(0)
    frame_count = 0

    while True: 
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, location in zip(face_encodings, face_locations):
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if len(distances) == 0:
                continue

            best_match_index = distances.argmin()
            name = "Unknown"
            if distances[best_match_index] < RECOGNITION_THRESHOLD:
                name = known_names[best_match_index]

                if name not in greeted_names:
                    # Crop face region for mood detection (from full frame)
                    top, right, bottom, left = [v * 4 for v in location]
                    face_crop = frame[top:bottom, left:right]

                    try:
                        result = DeepFace.analyze(face_crop, actions=['emotion'], enforce_detection=False)
                        mood = result[0]["dominant_emotion"]
                    except Exception as e:
                        print(f"[Emotion Detection Error] {e}")
                        mood = None

                    print(f"Greeting {name} with mood: {mood}")
                    greet_user(name, memory, current_command, mood)
                    greeted_names.add(name)
            else:
                if "Unknown" not in greeted_names:
                    speak("Hi there! I don't know you yet.")
                    current_command["action"] = "Hi there! I don't know you yet."
                    greeted_names.add("Unknown")
                    if SAVE_UNKNOWN:
                        save_unknown_face(frame)

            # Draw rectangle and name
            top, right, bottom, left = [v * 4 for v in location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Personal Greeter Bot', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break

    video_capture.release()
    cv2.destroyAllWindows()


# import os
# import cv2
# import pickle
# import face_recognition
# import pyttsx3
# import datetime
# import random
# import json

# # Paths
# KNOWN_FACES_DIR = "/Users/hassanchaudhry/Desktop/Ami/known_faces"
# ENCODING_FILE = "/Users/hassanchaudhry/Desktop/Ami/face_encodings.pkl"
# MEMORY_FILE = "visit_log.json"

# JOKES = [
#     "Why did the computer go to the doctor? It had a virus!",
#     "I'm not lazy, I'm on energy-saving mode.",
#     "Why did the robot cross the road? Because it was programmed by a chicken!",
#     "Beep boop! I'm smarter than I look.",
#     "Never trust atoms. They make up everything."
# ]

# def speak(text):
#     engine = pyttsx3.init() 
#     engine.say(text)
#     engine.runAndWait()

# def load_encodings(encoding_file):
#     with open(encoding_file, 'rb') as f:
#         return pickle.load(f)

# def load_memory():
#     if os.path.exists(MEMORY_FILE):
#         with open(MEMORY_FILE, "r") as f:
#             return json.load(f)
#     return {}

# def save_memory(memory):
#     with open(MEMORY_FILE, "w") as f:
#         json.dump(memory, f, indent=2)

# def greet_user(name, memory, current_command):
#     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     last_seen = memory.get(name)

#     if last_seen:
#         message = f"Welcome back, {name}! Last time I saw you was on {last_seen}." 
#     else:
#         message = f"Hello, {name}! Nice to meet you."

#     joke = random.choice(JOKES)
#     full_message = f"{message} {joke}"

#     speak(full_message)
#     current_command["action"] = full_message  # 👈 Robot will speak this via FastAPI

#     memory[name] = now
#     save_memory(memory)


# def recognize_and_greet(current_command):
#     known_encodings, known_names = load_encodings(ENCODING_FILE)
#     memory = load_memory()

#     video_capture = cv2.VideoCapture(0)
#     last_recognized = None

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#         face_locations = face_recognition.face_locations(rgb_small_frame)
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#         for face_encoding in face_encodings:
#             matches = face_recognition.compare_faces(known_encodings, face_encoding)
#             name = "Unknown"

#             if True in matches:
#                 index = matches.index(True)
#                 name = known_names[index]

#                 if last_recognized != name:
#                     print(f"Greeting {name}")
#                     greet_user(name, memory, current_command)
#                     last_recognized = name
#             else:
#                 if last_recognized != "Unknown":
#                     speak("Hi there! I don't know you yet.")
#                     current_command["action"] = "Hi there! I don't know you yet."  # 👈 Robot speaks
#                     last_recognized = "Unknown"

#         for (top, right, bottom, left) in face_locations:
#             top *= 4
#             right *= 4
#             bottom *= 4
#             left *= 4
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#         cv2.imshow('Personal Greeter Bot', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     video_capture.release()
#     cv2.destroyAllWindows()

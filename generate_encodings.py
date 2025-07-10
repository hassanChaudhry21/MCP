import face_recognition
import os
import pickle

known_face_encodings = []
known_face_names = []

folder = "/Users/hassanchaudhry/Desktop/Ami/known_faces"  # Path to your known faces folder

for filename in os.listdir(folder):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(folder, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])  # Use filename as name
        else:
            print(f"No faces found in {filename}")

# Save the encodings and names to a pickle file
with open('face_encodings.pkl', 'wb') as f:
    pickle.dump((known_face_encodings, known_face_names), f)

print("Face encodings saved to face_encodings.pkl")

file_path = "/Users/hassanchaudhry/Desktop/Ami/face_encodings.pkl"

# Load the pickle file
with open(file_path, "rb") as f:
    encodings, names = pickle.load(f)

# Print information
print(f"✅ Total faces encoded: {len(encodings)}")
print("✅ Names:")
for i, name in enumerate(names):
    print(f"  {i+1}. {name}")


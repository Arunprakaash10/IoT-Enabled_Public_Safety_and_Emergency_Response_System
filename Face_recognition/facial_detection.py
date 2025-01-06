import cv2
import face_recognition
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime

# PostgreSQL connection details (replace with your details)
db_config = {
    'host': '34.47.193.205',
    'port': '5432',
    'database': 'hons',
    'user': 'postgres',
    'password': 'hons_postgres'
}

# CSV file containing known faces and authorization status
CSV_FILE = "face_data.csv"

# Load face data from CSV
face_data = pd.read_csv(CSV_FILE)
known_names = face_data["Name"].values
known_authorized_status = face_data["Authorized"].values

# Load face encodings from the saved numpy file
known_face_encodings = np.load("face_encodings.npy", allow_pickle=True)

# Function to save detected person data to the PostgreSQL database
def save_detection_to_db(name, authorized, timestamp):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Insert detection record into the person_data table
        insert_query = """
        INSERT INTO person_data (name, authorized, timestamp)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (name, authorized, timestamp))
        
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Data saved: {name}, {'Authorized' if authorized else 'Unauthorized'}, {timestamp}")
    except Exception as e:
        print(f"Error saving to database: {e}")

# Initialize the webcam
video_capture = cv2.VideoCapture(0)

print("Face detection started. Press 'q' to quit.")

while True:
    # Capture frame-by-frame from the webcam
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to capture image.")
        break
    
    # Resize the frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces and compute face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the detected face with known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"
        authorized = False
        
        # Check if there's a match
        if True in matches:
            first_match_index = matches.index(True)  # Get the first match index
            name = known_names[first_match_index]
            # Get the authorization status from the CSV file
            authorized = bool(known_authorized_status[first_match_index])
        
        # Scale face locations back up to the original frame size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        
        # Draw a rectangle around the face
        color = (0, 255, 0) if authorized else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label with name and status
        label = f"{name} - {'Authorized' if authorized else 'Unauthorized'}"
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, label, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
        # Log and save data to the database
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_detection_to_db(name, authorized, timestamp)

    # Display the resulting frame
    cv2.imshow("Face Recognition", frame)

    # Wait for user input to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Release the webcam and close the OpenCV window
video_capture.release()
cv2.destroyAllWindows()
print("Face recognition stopped.")
import os
import face_recognition
import numpy as np
import pandas as pd

# Directory containing known faces organized by person name in subdirectories
KNOWN_FACES_DIR = "known_faces"

# CSV file to save training data
CSV_FILE = "face_data.csv"

# Initialize lists for storing data
face_encodings = []
face_names = []
face_authorized_status = []

# Load existing data from the CSV file, if it exists
if os.path.exists(CSV_FILE):
    face_data = pd.read_csv(CSV_FILE)
else:
    face_data = pd.DataFrame(columns=["Name", "Authorized"])

# Loop through each person in the known_faces directory
for person_name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, person_name)

    # Check if it's a directory
    if os.path.isdir(person_dir):
        # Check if the person already exists in the CSV file
        if person_name in face_data["Name"].values:
            print(f"{person_name} is already in the CSV file. Retraining with new images...")
            face_data = face_data[face_data["Name"] != person_name]  # Remove existing record to update
        else:
            # Prompt user for authorized/unauthorized status
            while True:
                status_input = input(f"Is {person_name} authorized? (yes/no): ").strip().lower()
                if status_input in ('yes', 'no'):
                    is_authorized = True if status_input == 'yes' else False
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

        # Process each image file in the person's directory
        for filename in os.listdir(person_dir):
            image_path = os.path.join(person_dir, filename)

            # Check if the file is an image
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    # Load the image file
                    image = face_recognition.load_image_file(image_path)
                    
                    # Get face encodings
                    encodings = face_recognition.face_encodings(image)
                    
                    # If an encoding is found, add it to our lists
                    if encodings:
                        print(f"Processed image: {image_path}")
                        face_encodings.append(encodings[0])  # Save only one encoding per person
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
        
        # Save the person's data (single record)
        face_names.append(person_name)
        face_authorized_status.append(is_authorized)

# Convert the new data to a DataFrame
new_face_data = pd.DataFrame({
    "Name": face_names,
    "Authorized": face_authorized_status
})

# Combine existing and new data, ensuring there are no duplicates
updated_face_data = pd.concat([face_data, new_face_data], ignore_index=True)

# Save the combined data back to the CSV file
updated_face_data.to_csv(CSV_FILE, index=False)

# Save face encodings to a NumPy file (optional, if needed later for detection)
face_encodings = np.array(face_encodings)
np.save("face_encodings.npy", face_encodings)

print(f"Training complete. Data saved to {CSV_FILE}.")
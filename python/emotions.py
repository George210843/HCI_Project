import cv2
from deepface import DeepFace

# Load the pre-trained emotion detection model
model = DeepFace.build_model("Emotion")

# Define emotion labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


path = '/txtfiles/emotions.txt'

# Create a text file to store the detected emotions
emotion_file = open(path, "a")

# Open the video file
video_file_path = '/videos/neutral.mp4'
cap = cv2.VideoCapture(video_file_path)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Extract the face ROI (Region of Interest)
        face_roi = gray_frame[y:y + h, x:x + w]

        # Resize the face ROI to match the input shape of the model
        resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)

        # Normalize the resized face image
        normalized_face = resized_face / 255.0

        # Reshape the image to match the input shape of the model
        reshaped_face = normalized_face.reshape(1, 48, 48, 1)

        # Predict emotions using the pre-trained model
        preds = model.predict(reshaped_face)[0]
        emotion_idx = preds.argmax()
        emotion = emotion_labels[emotion_idx]

        # Display the detected emotion in the window
        cv2.putText(frame, "Emotion: " + emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Write the detected emotion to the text file
        emotion_file.write(emotion + "\n")

  

# Release the capture, close the text file, and close all windows
cap.release()
emotion_file.close()
cv2.destroyAllWindows()

# Read the text file with detected emotions
with open(path, "r") as emotion_file:
    emotions = emotion_file.read().splitlines()

# Count the occurrences of each emotion
emotion_count = {}
for emotion in emotions:
    if emotion in emotion_count:
        emotion_count[emotion] += 1
    else:
        emotion_count[emotion] = 1

# Find the most frequent emotion
most_frequent_emotion = max(emotion_count, key=emotion_count.get)

# Send the most frequent emotion (you can replace this with your desired method of sending)
print("Most frequent emotion:", most_frequent_emotion)
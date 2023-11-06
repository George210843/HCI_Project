import socket
import cv2
from dollarpy import Point, Recognizer, Template
import mediapipe as mp
import socket

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

templates = []  # List of templates for $1 training

# Function to capture points for a given video and label
def getPoints(videoURL, label):
    cap = cv2.VideoCapture(videoURL)
    points = []

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()

            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                          )
                

                try:
                    pose = results.pose_landmarks.landmark
                    points.extend([Point(lnd.x, lnd.y, i + 1) for i, lnd in enumerate(pose) if i in range(11)])

                except:
                    pass

                cv2.imshow(label, image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    print(label)
    return points

# Capture points for explaining and sitting
vid_explaining = 'Explaining.mp4'
points_explaining = getPoints(vid_explaining, "Explaining")
tmpl_explaining = Template('Explaining', points_explaining)
templates.append(tmpl_explaining)

vid_sitting = 'Sitting.mp4'
points_sitting = getPoints(vid_sitting, "Sitting")
tmpl_sitting = Template('Sitting', points_sitting)
templates.append(tmpl_sitting)

# Function to classify movement
def classify():
    recognizer = Recognizer(templates)
    cap = cv2.VideoCapture(0)

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()

            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                wrist_x1 = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                wrist_y1 = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

                normalized_x = wrist_x1 * 100
                normalized_y = wrist_y1 * 100
                wrist_x = round(normalized_x)
                wrist_y = round(normalized_y)
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                          )
                wrist_coordinates = f"Wrist X: {wrist_x}, Wrist Y: {wrist_y}"
                mySocket = socket.socket()
                mySocket.connect(('localhost', 5000))
                msg=bytes(wrist_coordinates,'utf-8')
                mySocket.send(msg)
                mySocket.close()
                try:
                    pose = results.pose_landmarks.landmark
                    points = [Point(lnd.x, lnd.y, i + 1) for i, lnd in enumerate(pose) if i in range(11)]
                    result = recognizer.recognize(points)
                    print(result)
                    

                except:
                    pass
                cv2.imshow("Classification", image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# Run the classification
classify()

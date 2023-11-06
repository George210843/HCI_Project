import cv2
import dlib

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    
    for face in faces:

        landmarks = predictor(gray, face)
        
        left_eye_x, left_eye_y = landmarks.part(36).x, landmarks.part(36).y
        right_eye_x, right_eye_y = landmarks.part(45).x, landmarks.part(45).y
        
        face_direction = (right_eye_x - left_eye_x, right_eye_y - left_eye_y)
        
        cv2.line(frame, (left_eye_x, left_eye_y), (right_eye_x, right_eye_y), (0, 255, 0), 2)
        
    cv2.imshow('Face Direction Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()

import ultralytics
ultralytics.__version__

from ultralytics import YOLO


from ultralytics.yolo.v8.detect.predict import DetectionPredictor

import cv2

model=YOLO("yolov8s.pt")

result=model.predict(source="0",show=True)

print(result)
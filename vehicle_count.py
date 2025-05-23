import cv2
from ultralytics import YOLO
import numpy as np
from collections import defaultdict, deque

#Use yolov8m.pt or yolov8x.pt for increased accuracy
model = YOLO('yolov8s.pt')

with open('coco.names', 'r') as f:
    coco_names = [line.strip() for line in f.readlines()]

video_path = 'video.mp4'
cap = cv2.VideoCapture(video_path)

# Resize info
width, height = 1280, 720

# Line position
line_position = 360

# Counters
counter_up = 0
counter_down = 0
counted_ids = set()

track_history = defaultdict(lambda: deque(maxlen=2))

# Vehicle class IDs in COCO set
vehicle_class_ids = [2, 3, 5, 7]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (width, height))

    # Run YOLO tracking
    results = model.track(
        frame,
        persist=True,
        classes=vehicle_class_ids,
        conf=0.4,
        iou=0.5
    )

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        ids = results[0].boxes.id.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy()

        for box, obj_id, class_id in zip(boxes, ids, class_ids):
            x1, y1, x2, y2 = box.astype(int)
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

            label = coco_names[int(class_id)]
            track_history[obj_id].append(cy)

            if len(track_history[obj_id]) == 2:
                y_prev, y_curr = track_history[obj_id]

                if y_prev < line_position <= y_curr and obj_id not in counted_ids:
                    counter_down += 1
                    counted_ids.add(obj_id)

                elif y_prev > line_position >= y_curr and obj_id not in counted_ids:
                    counter_up += 1
                    counted_ids.add(obj_id)

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(frame, f'{label} ID:{int(obj_id)}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Draw the counting line
    cv2.line(frame, (0, line_position), (width, line_position), (255, 0, 0), 2)

    # Draw counters
    cv2.putText(frame, f'Up: {counter_up}', (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f'Down: {counter_down}', (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show the frame (generate output)
    cv2.imshow('Vehicle Detection and Counting', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

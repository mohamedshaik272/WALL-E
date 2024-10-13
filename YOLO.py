import torch
from PIL import Image

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Custom class names for trash detection
model.names = ['plastic', 'paper', 'glass']

def detect_trash(image_path):
    # Load the image
    img = Image.open(image_path)
    
    # Perform inference
    results = model(img)
    
    # Process results
    detections = results.xyxy[0]  # tensor of detections
    
    trash_items = []
    for detection in detections:
        class_id = int(detection[5])
        confidence = float(detection[4])
        if confidence > 0.5:  # Confidence threshold
            trash_items.append(model.names[class_id])
    
    return trash_items

# Example usage
image_path = 'path/to/your/image.jpg'
detected_trash = detect_trash(image_path)

if detected_trash:
    print(f"Detected trash items: {', '.join(detected_trash)}")
else:
    print("No trash items detected.")
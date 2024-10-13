import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import requests
import os
import time
import serial

# Arduino setup and communication
arduino_port = '/dev/ttyACM0'
baud_rate = 9600

def init_arduino():
    try:
        arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the connection to establish
        return arduino
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

arduino = init_arduino()
if arduino is None:
    print("Error: Could not initialize the Arduino. Please check your connection and port settings.")
    exit(1)

def test_arduino_communication():
    print("Testing Arduino communication...")
    arduino.write(b't\n')  # Send test command
    time.sleep(1)
    response = arduino.readline().decode().strip()
    print(f"Arduino response: {response}")
    if response == "Test OK":
        print("Arduino communication test successful")
    else:
        print("Arduino communication test failed")

test_arduino_communication()

def send_arduino_command(command):
    print(f"Sending command to Arduino: {command}")
    arduino.write(command.encode() + b'\n')
    time.sleep(0.1)  # Short delay after sending command
    response = arduino.readline().decode().strip()
    print(f"Arduino response: {response}")
    return response

# Download the model if not already present
model_url = "https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip"
model_path = "detect.tflite"
labels_path = "labelmap.txt"

if not (os.path.exists(model_path) and os.path.exists(labels_path)):
    import zipfile
    import io
    print("Downloading model...")
    r = requests.get(model_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(".")
    print("Model downloaded and extracted.")

# Load the TFLite model
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Initialize camera
def init_camera():
    for i in range(10):  # Try the first 10 video devices
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            print(f"Successfully opened camera device {i}")
            return camera
    print("Failed to open any camera device")
    return None

camera = init_camera()
if camera is None:
    print("Error: Could not initialize the camera. Please check your camera connection and permissions.")
    exit(1)

# Load labels
with open(labels_path, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

def detect_brown_object(frame):
    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define range for brown color
    lower_brown = np.array([10, 100, 20])
    upper_brown = np.array([20, 255, 200])
    
    # Create a mask for brown color
    mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Calculate the percentage of brown pixels
    brown_pixel_count = cv2.countNonZero(mask)
    total_pixels = frame.shape[0] * frame.shape[1]
    brown_percentage = (brown_pixel_count / total_pixels) * 100
    
    if brown_percentage > 50:
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            return (x, y, w, h), brown_percentage
    
    return None, brown_percentage

def detect_object():
    ret, frame = camera.read()
    if not ret:
        print("Failed to capture image")
        return False, None, None, 0

    # Check for brown object
    brown_object, brown_percentage = detect_brown_object(frame)
    if brown_object is not None:
        x, y, w, h = brown_object
        # Draw rectangle and label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        label = f"Paper: {brown_percentage:.0f}%"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        print(f"Detected: Large brown object covering {brown_percentage:.0f}% of the screen")
        print("Category: Paper")
        print(f"Confidence: {brown_percentage:.0f}%")
        return True, frame, "Paper", brown_percentage

    # If no large brown object detected, use the TFLite model
    input_shape = input_details[0]['shape'][1:3]
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, input_shape)
    image = np.expand_dims(image_resized, axis=0).astype(np.uint8)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], image)
    interpreter.invoke()

    # Get detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    classes = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    # Find the detection with highest confidence
    max_score_index = np.argmax(scores)
    if scores[max_score_index] > 0.2:  # Lowered confidence threshold
        detected_class = labels[int(classes[max_score_index])]
        
        # Get the bounding box
        y_min, x_min, y_max, x_max = boxes[max_score_index]
        h, w, _ = frame.shape
        bbox = (int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h))
        
        # Calculate the area of the bounding box
        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        frame_area = h * w
        
        # Adjust confidence if the object takes up more than half the screen
        base_confidence = scores[max_score_index] * 100
        if bbox_area > (frame_area / 2):
            confidence = min(base_confidence + 40, 100)  # Add 40 percentage points (0.4 * 100)
        else:
            confidence = base_confidence
        
        # Draw bounding box and label
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        label = f"{detected_class}: {confidence:.0f}%"
        cv2.putText(frame, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        print(f"Detected: {detected_class}")
        print(f"Confidence: {confidence:.0f}%")
        return True, frame, detected_class, confidence
    else:
        print("No object detected with sufficient confidence")
    
    return False, frame, None, 0

# Ensure 'images' directory exists
if not os.path.exists('images'):
    os.makedirs('images')

# Main execution
try:
    print("Starting detection. Press Ctrl+C to exit.")
    detection_count = 0
    while camera.isOpened():
        detection_count += 1
        print(f"\nAttempt {detection_count}: Scanning for objects...")
        detected, frame, detected_class, confidence = detect_object()
        
        if detected:
            # Save the image
            timestamp = int(time.time())
            image_path = f"images/detection_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)
            print(f"Image saved: {image_path}")
            
            if confidence >= 80:
                print(f"Object detected with {confidence:.0f}% confidence. Labeling as {detected_class}.")
                print("Sending forward command to Arduino...")
                response = send_arduino_command('f')
                if response != "Moving forward":
                    print("Warning: Unexpected response from Arduino")
                time.sleep(10)  # Move forward for 10 seconds
                print("Sending stop command to Arduino...")
                response = send_arduino_command('s')
                if response != "Stopped":
                    print("Warning: Unexpected response from Arduino")
                break  # Exit the loop after sending the signal
            else:
                print(f"Detected {detected_class} with {confidence:.0f}% confidence. Continuing...")
        else:
            print("No object detected in this scan.")
        time.sleep(1)  # Delay between detections
except KeyboardInterrupt:
    print("Detection stopped by user.")
finally:
    print("Cleaning up...")
    if camera is not None:
        camera.release()
    cv2.destroyAllWindows()
    if arduino is not None:
        arduino.close()
    print("Program ended.")
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

def detect_brown_paper(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_brown = np.array([5, 50, 50])
    upper_brown = np.array([30, 255, 200])
    mask = cv2.inRange(hsv, lower_brown, upper_brown)
    brown_pixel_count = cv2.countNonZero(mask)
    total_pixels = frame.shape[0] * frame.shape[1]
    brown_percentage = (brown_pixel_count / total_pixels) * 100
    
    if brown_percentage > 20:  # Lowered threshold
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            return (x, y, w, h), brown_percentage
    
    return None, brown_percentage

def detect_redbull_can(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_pixel_count = cv2.countNonZero(mask)
    total_pixels = frame.shape[0] * frame.shape[1]
    blue_percentage = (blue_pixel_count / total_pixels) * 100
    
    if blue_percentage > 5:  # Increased threshold
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = h / w
            if 1.5 < aspect_ratio < 3.5:
                return (x, y, w, h), blue_percentage
    
    return None, blue_percentage

def detect_large_object(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        object_area = w * h
        frame_area = frame.shape[0] * frame.shape[1]
        
        # Adjust these thresholds as needed
        if object_area > frame_area * 0.3 and object_area < frame_area * 0.8:
            aspect_ratio = h / w
            if 0.5 < aspect_ratio < 2.0:  # This allows for objects that aren't too elongated
                return (x, y, w, h)
    
    return None

def detect_object():
    ret, frame = camera.read()
    if not ret:
        print("Failed to capture image")
        return False, None, None, 0, 0, 0

    brown_object, brown_percentage = detect_brown_paper(frame)
    redbull_object, blue_percentage = detect_redbull_can(frame)
    large_object = detect_large_object(frame)
    
    if brown_object is not None:
        x, y, w, h = brown_object
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        label = f"Brown Paper: {brown_percentage:.0f}%"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        print(f"Detected: Brown paper covering {brown_percentage:.0f}% of the screen")
        return True, frame, "Brown Paper", brown_percentage, brown_percentage, blue_percentage

    if redbull_object is not None:
        x, y, w, h = redbull_object
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        label = f"Red Bull: {blue_percentage:.0f}%"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        print(f"Detected: Red Bull can with {blue_percentage:.0f}% blue content")
        return True, frame, "Red Bull", blue_percentage, brown_percentage, blue_percentage

    if large_object is not None:
        x, y, w, h = large_object
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        label = "Large Object"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        print("Detected: Large object within specified size and aspect ratio")
        return True, frame, "Large Object", 100, brown_percentage, blue_percentage

    print("No object detected")
    return False, frame, None, 0, brown_percentage, blue_percentage

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
        detected, frame, detected_class, confidence, brown_percentage, blue_percentage = detect_object()
        
        timestamp = int(time.time())
        image_path = f"images/detection_{timestamp}.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Image saved: {image_path}")
        
        if detected:
            if detected_class == "Brown Paper" or (detected_class == "Large Object" and brown_percentage > blue_percentage):
                print(f"{detected_class} detected. Sending 'f' command to Arduino...")
                response = send_arduino_command('f')
                if response != "Moving Forward and Back":
                    print("Warning: Unexpected response from Arduino")
                break  # Stop after sending command
            elif detected_class == "Red Bull" or (detected_class == "Large Object" and blue_percentage > brown_percentage):
                print(f"{detected_class} detected. Sending 'r' command to Arduino...")
                response = send_arduino_command('r')
                if response != "Moving Right and Back":
                    print("Warning: Unexpected response from Arduino")
                break  # Stop after sending command
            else:
                print(f"Detected {detected_class} but no action taken.")
        else:
            print(f"No clear detection. Brown: {brown_percentage:.0f}%, Blue: {blue_percentage:.0f}%")
        
        time.sleep(1)  # Delay between detections
except KeyboardInterrupt:
    print("Detection stopped by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Cleaning up...")
    if camera is not None:
        camera.release()
    cv2.destroyAllWindows()
    if arduino is not None:
        arduino.close()
    print("Program ended.")
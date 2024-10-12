import os
import time
import shutil
import mimetypes
from openai import OpenAI
from datetime import datetime
from PIL import Image
import pytesseract
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_file_category(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        category = mime_type.split('/')[0]
        return category if category != 'application' else 'documents'
    return 'others'

def extract_text_from_image(image_path):
    try:
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img)
        return text[:1000]  # Return first 1000 characters
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {str(e)}")
        return ""

def get_file_content(file_path, max_chars=1000):
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('image'):
            return extract_text_from_image(file_path)
        with open(file_path, 'rb') as file:
            raw_content = file.read(max_chars)
        return raw_content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return ""

def suggest_filename(file_path):
    content = get_file_content(file_path)
    if not content:
        return None
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that suggests concise and descriptive filenames based on file content. Suggest only the filename without any explanation."},
                {"role": "user", "content": f"Suggest a concise and descriptive filename for a file with the following content:\n\n{content}"}
            ]
        )
        suggested_name = response.choices[0].message.content.strip()
        return suggested_name
    except Exception as e:
        print(f"Error suggesting filename for {file_path}: {str(e)}")
        return None

def sanitize_filename(filename):
    return ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()

def clean_up_file(file_path, archive_dir):
    # Move the file to an 'archive' folder
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, os.path.basename(file_path))
    shutil.move(file_path, archive_path)
    print(f"Archived: {file_path} -> {archive_path}")

def organize_directory(directory):
    archive_dir = os.path.join(directory, 'archive')
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            last_accessed = os.path.getatime(file_path)
            
            if time.time() - last_accessed > 30 * 24 * 60 * 60:  # 30 days
                clean_up_file(file_path, archive_dir)
            else:
                # Get file category
                category = get_file_category(file_path)
                
                # Create category folder
                category_path = os.path.join(directory, category)
                os.makedirs(category_path, exist_ok=True)
                
                # Suggest new filename
                new_name = suggest_filename(file_path)
                if new_name:
                    new_name = sanitize_filename(new_name)
                    file_extension = os.path.splitext(file)[1]
                    new_file_path = os.path.join(category_path, new_name + file_extension)
                    
                    # Handle filename conflicts
                    counter = 1
                    while os.path.exists(new_file_path):
                        new_file_path = os.path.join(category_path, f"{new_name}_{counter}{file_extension}")
                        counter += 1
                else:
                    new_file_path = os.path.join(category_path, file)
                
                # Move and rename file
                shutil.move(file_path, new_file_path)
                print(f"Moved and renamed: {file} -> {new_file_path}")

if __name__ == "__main__":
    target_directory = input("Enter the directory path to organize: ")
    organize_directory(target_directory)
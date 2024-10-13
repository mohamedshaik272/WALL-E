import os
import time
import shutil
import mimetypes
import hashlib
from openai import OpenAI
from datetime import datetime
from PIL import Image
import pytesseract
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#"gpt-3.5-turbo"

def get_ai_categorization_scheme(user_description):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that helps users organize their files. Based on the user's description, create a categorization scheme that maps file types to category names and subcategories. Use precise category names, for example, code files should be named 'Code' or 'Programming' instead of 'Text'. Respond with a Python dictionary where keys are file extensions or MIME types, and values are lists containing the main category and subcategories."},
                {"role": "user", "content": f"Create a file categorization scheme based on this description: {user_description}"}
            ]
        )
        categorization_scheme = eval(response.choices[0].message.content.strip())
        return categorization_scheme
    except Exception as e:
        print(f"Error generating categorization scheme: {str(e)}")
        return {}

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_file_category(file_path, user_categories):
    if not user_categories:
        # Default categorization if no user categories are defined
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            category = mime_type.split('/')[0]
            return [category if category != 'application' else 'documents']
        return ['others']

    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() in user_categories:
        return user_categories[ext.lower()]

    # Check mime type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type in user_categories:
        return user_categories[mime_type]

    # Check general mime type category
    if mime_type:
        general_type = mime_type.split('/')[0]
        if general_type in user_categories:
            return user_categories[general_type]

    # Consider drawings as images
    if mime_type and mime_type.startswith('application/drawing'):
        return ['Images']

    return ['Others']

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
                {"role": "system", "content": "You are a helpful assistant that suggests concise and descriptive filenames based on file content. Suggest only the filename without any explanation or file extension. Max 25 characters"},
                {"role": "user", "content": f"Suggest a concise and descriptive filename for a file with the following content:\n\n{content}"}
            ]
        )
        suggested_name = response.choices[0].message.content.strip()
        return suggested_name
    except Exception as e:
        print(f"Error suggesting filename for {file_path}: {str(e)}")
        return None

def sanitize_filename(filename):
    # Sanitize the filename
    sanitized = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return sanitized

def should_rename_file(file_path):
    # List of file types that shouldn't be renamed
    no_rename_extensions = ['.exe', '.app', '.iso']
    _, ext = os.path.splitext(file_path)
    if ext.lower() in no_rename_extensions:
        return False
    return True

def review_code_file(file_path):
    content = get_file_content(file_path)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code reviewer. Review the following code and provide a brief summary of its functionality."},
                {"role": "user", "content": f"Review this code:\n\n{content}"}
            ]
        )
        review = response.choices[0].message.content.strip()
        return review
    except Exception as e:
        print(f"Error reviewing code file {file_path}: {str(e)}")
        return "Unable to review the file."

def is_file_old(file_path, days_threshold=365):
    """Check if a file hasn't been accessed in a long time."""
    current_time = datetime.now().timestamp()
    last_access_time = os.path.getmtime(file_path)
    return (current_time - last_access_time) > (days_threshold * 24 * 60 * 60)

def is_content_useless(file_path):
    """Analyze file content to determine if it's useless."""
    content = get_file_content(file_path)
    if not content:
        return False  # If we can't read the content, we assume it's not useless

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that analyzes file content to determine if it's useless. Useless files: Content in a non english language, any way associated with junk, installers. Respond with 'YES' if the content is useless or 'NO' if it might be valuable."},
                {"role": "user", "content": f"Is the following file content useless?\n\n{content}"}
            ]
        )
        return response.choices[0].message.content.strip().upper() == "YES"
    except Exception as e:
        print(f"Error analyzing content usefulness for {file_path}: {str(e)}")
        return False

def organize_directory(directory, user_categories):
    hash_dict = {}
    for root, dirs, files in os.walk(directory):
        # Ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # Ignore hidden files
            if file.startswith('.'):
                continue
            
            file_path = os.path.join(root, file)

            old = is_file_old(file_path)
            useless = is_content_useless(file_path)

            # Check if file is old and potentially useless
            if old and useless:
                os.remove(file_path)
                print(f"Removed old and useless file: {file_path}")
                continue
            # Check if file is old
            elif old:
                os.remove(file_path)
                print(f"Removed old file: {file_path}")
                continue
            # Check if file is potentially useless
            elif useless:
                os.remove(file_path)
                print(f"Removed useless file: {file_path}")
                continue

            file_hash = get_file_hash(file_path)
            
            if file_hash in hash_dict:
                # This is a duplicate, remove it
                os.remove(file_path)
                print(f"Removed duplicate: {file_path}")
                continue
            
            hash_dict[file_hash] = file_path
            
            # Remove .dmg files by default
            if file.endswith('.dmg'):
                os.remove(file_path)
                print(f"Removed .dmg file: {file_path}")
                continue
            
            # Get file category and subcategories
            categories = get_file_category(file_path, user_categories)
            
            # Handle code files (.c, .java, etc.)
            _, ext = os.path.splitext(file)
            if ext.lower() in ['.c', '.java', '.py', '.cpp', '.h', '.js', '.cs']:
                review = review_code_file(file_path)
                print(f"Code file review for {file}:\n{review}")
                categories = ['Code']
            
            # Create category and subcategory folders
            category_path = os.path.join(directory, *categories)
            os.makedirs(category_path, exist_ok=True)
            
            # Suggest new filename if appropriate
            if should_rename_file(file_path):
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
                    new_file_path = os.path.join(category_path, sanitize_filename(os.path.splitext(file)[0]) + os.path.splitext(file)[1])
            else:
                new_file_path = os.path.join(category_path, file)
            
            # Move and rename file
            shutil.move(file_path, new_file_path)
            print(f"Moved and renamed: {file} -> {new_file_path}")

    # After organizing, delete empty folders
    delete_empty_folders(directory)

def delete_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                if not os.listdir(dir_path):  # Check if the directory is empty
                    os.rmdir(dir_path)
                    print(f"Deleted empty folder: {dir_path}")
            except Exception as e:
                print(f"Error deleting folder {dir_path}: {str(e)}")

if __name__ == "__main__":
    target_directory = input("Enter the directory path to organize: ")
    
    # Ask user if they want to use custom categorization
    use_custom_categories = input("Do you want to use a custom directory organization scheme? (y/n): ").lower() == 'y'
    
    categorization_scheme = {}
    if use_custom_categories:
        user_description = input("Describe how you'd like your files organized (e.g., 'I want my photos, documents, and code files separated'): ")
        categorization_scheme = get_ai_categorization_scheme(user_description)
        print("Generated categorization scheme:", categorization_scheme)
    
    organize_directory(target_directory, categorization_scheme)
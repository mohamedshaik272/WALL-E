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

def get_ai_categorization_scheme(user_description):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that helps users organize their files. Based on the user's description, create a categorization scheme that maps file types to category names. Use precise category names, for example, code files should be named 'Code' or 'Programming' instead of 'Text'. Respond with a Python dictionary where keys are file extensions or MIME types, and values are category names."},
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
            return category if category != 'application' else 'documents'
        return 'others'

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

    return 'Others'

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

def suggest_filename(file_path, naming_convention):
    content = get_file_content(file_path)
    if not content:
        return None
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that suggests concise and descriptive filenames based on file content. Use the {naming_convention} naming convention. Suggest only the filename without any explanation."},
                {"role": "user", "content": f"Suggest a concise and descriptive filename for a file with the following content:\n\n{content}"}
            ]
        )
        suggested_name = response.choices[0].message.content.strip()
        return suggested_name
    except Exception as e:
        print(f"Error suggesting filename for {file_path}: {str(e)}")
        return None
def get_custom_categories():
    user_categories = {}
    print("Enter custom categories. Format: 'mime_type: category_name'")
    print("Example: 'image: pictures' or 'application/pdf: documents'")
    print("Press Enter without typing anything when you're done.")
    while True:
        category = input("Enter a custom category (or press Enter to finish): ").strip()
        if not category:
            break
        try:
            mime_type, category_name = [item.strip() for item in category.split(':', 1)]
            if not mime_type or not category_name:
                print("Invalid format. Please use 'mime_type: category_name'.")
                continue
            user_categories[mime_type] = category_name
        except ValueError:
            print("Invalid format. Please use 'mime_type: category_name'.")
    return user_categories

def sanitize_filename(filename):
    return ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()

def should_rename_file(file_path):
    # List of file types that shouldn't be renamed
    no_rename_extensions = ['.exe', '.app', '.dmg', '.iso']
    _, ext = os.path.splitext(file_path)
    if ext.lower() in no_rename_extensions:
        return False
    # Add more conditions here if needed
    return True

def organize_directory(directory, user_categories, naming_convention, remove_dmg):
    hash_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            
            if file_hash in hash_dict:
                # This is a duplicate, remove it
                os.remove(file_path)
                print(f"Removed duplicate: {file_path}")
                continue
            
            hash_dict[file_hash] = file_path
            
            # Remove .dmg files if specified
            if remove_dmg and file.endswith('.dmg'):
                os.remove(file_path)
                print(f"Removed .dmg file: {file_path}")
                continue
            
            # Get file category
            category = get_file_category(file_path, user_categories)
            
            # Create category folder
            category_path = os.path.join(directory, category)
            os.makedirs(category_path, exist_ok=True)
            
            # Suggest new filename if appropriate
            if should_rename_file(file_path):
                new_name = suggest_filename(file_path, naming_convention)
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
            else:
                new_file_path = os.path.join(category_path, file)
            
            # Move and rename file
            shutil.move(file_path, new_file_path)
            print(f"Moved and renamed: {file} -> {new_file_path}")

if __name__ == "__main__":
    target_directory = input("Enter the directory path to organize: ")
    
    # Ask user if they want to use custom categorization
    use_custom_categories = input("Do you want to use a custom directory organization scheme? (y/n): ").lower() == 'y'
    
    categorization_scheme = {}
    if use_custom_categories:
        user_description = input("Describe how you'd like your files organized (e.g., 'I want my photos, documents, and code files separated'): ")
        categorization_scheme = get_ai_categorization_scheme(user_description)
        print("Generated categorization scheme:", categorization_scheme)
    
    # Ask user for naming convention
    print("\nChoose a naming convention:")
    print("1. camelCase")
    print("2. snake_case")
    print("3. kebab-case")
    print("4. PascalCase")
    naming_choice = input("Enter your choice (1-4): ")
    naming_conventions = {
        '1': 'camelCase',
        '2': 'snake_case',
        '3': 'kebab-case',
        '4': 'PascalCase'
    }
    naming_convention = naming_conventions.get(naming_choice, 'snake_case')
    
    # Ask if user wants to remove .dmg files
    remove_dmg = input("Do you want to remove .dmg files? (y/n): ").lower() == 'y'
    
    organize_directory(target_directory, categorization_scheme, naming_convention, remove_dmg)
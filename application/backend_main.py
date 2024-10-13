import os
import shutil
import mimetypes
import hashlib
from openai import OpenAI
from datetime import datetime
from PIL import Image
import pytesseract
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
Generates a file categorization scheme based on a user's description.

This function interacts with the GPT-3.5 model to create a categorization scheme that maps file types to specific categories. 
The function takes a user's description of their categorization needs and returns a Python dictionary
with file extensions or MIME types as keys and a list containing the main category and subcategories as values.

Args:
    user_description (str): A textual description provided by the user detailing their file organization preferences.

Returns:
    dict: A dictionary where the keys are file extensions or MIME types, and the values are lists with the main category
        and subcategories. If an error occurs, an empty dictionary is returned.
          
Raises:
    Exception: Catches and logs any errors that occur during the interaction with the GPT model.
"""
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

"""
Generates an MD5 hash for a given file.

This function calculates the MD5 hash of a file.
It reads the file in binary mode, processes its contents, and returns the hash as a hexadecimal string.

Args:
    file_path (str): The path to the file for which the hash is to be computed.

Returns:
    str: The MD5 hash of the file as a hexadecimal string.
"""
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

"""
Categorizes a file based on user-defined categories or MIME types.

This function assigns a file to a category based on the file's extension or MIME type. 
If the user has provided a custom categorization scheme, the function will use that; 
otherwise, it defaults to general categories like "documents", "images", or "others".

Args:
    file_path (str): The path to the file to be categorized.
    user_categories (dict): A dictionary mapping file extensions, MIME types, or general types to categories. 
        Keys can be file extensions (e.g., '.txt'), MIME types (e.g., 'text/plain'), or general types (e.g., 'image').

Returns:
    list: A list containing the main category (and possibly subcategories) for the file.
        If the file type is not recognized, it returns a default category like 'Others'.
"""
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

"""
This function uses the Tesseract OCR engine to extract text from an image.
The extracted text is returned as a string, with a limit of the first 1000 characters.

Args:
    image_path (str): The path to the image file from which text needs to be extracted.

Returns:
    str: A string containing the first 1000 characters of the extracted text. If an error occurs during extraction, an empty string is returned.

Raises:
    Exception: Catches and logs any errors that occur during the image reading or text extraction process.
"""
def extract_text_from_image(image_path):
    try:
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img)
        return text[:1000] 
    except Exception as e:
        print(f"Error extracting text from image {image_path}: {str(e)}")
        return ""

"""
Extracts text from a PDF file.

This function uses a PDF reader to extract text from a PDF document. It processes the pages sequentially, 
accumulating text until the specified character limit (`max_chars`) is reached or the end of the PDF is reached. If an error occurs during 
the extraction process, an empty string is returned.

Args:
    file_path (str): The path to the PDF file from which text needs to be extracted.
    max_chars (int, optional): The maximum number of characters to extract from the PDF. Defaults to 1000.

Returns:
    str: The extracted text from the PDF, limited to `max_chars` characters. 
        If an error occurs during extraction, an empty string is returned.

Raises:
    Exception: Catches and logs any errors that occur during the PDF text extraction process.
"""
def extract_text_from_pdf(file_path, max_chars=1000):
    try:
        # Open the PDF using PdfReader
        reader = PdfReader(file_path)
        extracted_text = ""

        # Loop through pages and extract text
        for page in reader.pages:
            extracted_text += page.extract_text()

            # Stop if max_chars is reached
            if len(extracted_text) >= max_chars:
                extracted_text = extracted_text[:max_chars]
                break

        return extracted_text
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

"""
Extracts content from a file based on its type.

This function retrieves the content of a file depending on its type. 
For image files, it uses OCR to extract text. For PDFs, it uses a dedicated PDF extraction method. 
For all other files, it reads and decodes the raw content.

Args:
    file_path (str): The path to the file from which content needs to be extracted.
    max_chars (int, optional): The maximum number of characters to extract from the file. Defaults to 1000.

Returns:
    str: The extracted content as a string. If the file is an image or a PDF, the extracted text is returned. 
        For other files, the function returns the raw content as a string (up to `max_chars`).
        If an error occurs, an empty string is returned.

Raises:
    Exception: Catches and logs any errors that occur during file reading or content extraction.
"""
def get_file_content(file_path, max_chars=1000):
    try:
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type and mime_type.startswith('image'):
            return extract_text_from_image(file_path)

        if mime_type and mime_type == 'application/pdf':
            return extract_text_from_pdf(file_path, max_chars)

        with open(file_path, 'rb') as file:
            raw_content = file.read(max_chars)
        return raw_content.decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return ""

"""
Suggests a filename based on the content of a file.

This function analyzes the content of a file and uses a GPT-3.5 model to generate a filename suggestion. 
The filename is meant to be max 20 characters and descriptive of the file's content.

Args:
    file_path (str): The path to the file for which a filename suggestion is needed.

Returns:
    str: A filename based on the file's content.
        If an error occurs or the content cannot be extracted, None is returned.

Raises:
    Exception: Catches and logs any errors that occur during the filename suggestion process.
"""
def suggest_filename(file_path):
    content = get_file_content(file_path)
    if not content:
        return None
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that suggests concise and descriptive filenames based on file content. Suggest only the filename without any explanation or file extension. Max 20 characters"},
                {"role": "user", "content": f"Suggest a concise and descriptive filename for a file with the following content:\n\n{content}"}
            ]
        )
        suggested_name = response.choices[0].message.content.strip()
        return suggested_name
    except Exception as e:
        print(f"Error suggesting filename for {file_path}: {str(e)}")
        return None

"""
Sanitizes a filename by removing invalid characters.

This function cleans up a filename by keeping only alphanumeric characters, spaces, hyphens, 
and underscores. It removes any other characters that may not be allowed in filenames on most file systems, 
and trims any trailing whitespace.

Args:
    filename (str): The filename to be sanitized.

Returns:
    str: A sanitized version of the filename.
"""
def sanitize_filename(filename):
    sanitized = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return sanitized

"""
Determines whether a file should be renamed based on its extension.

This function checks the file extension to decide if renaming is appropriate. 
Certain file types, like executables and disk images (e.g., .exe, .app, .iso), 
are excluded from renaming.

Args:
    file_path (str): The path to the file being checked.

Returns:
    bool: Returns True if the file can be renamed, False if it is one of the excluded types.
"""
def should_rename_file(file_path):
    no_rename_extensions = ['.exe', '.app', '.iso']
    _, ext = os.path.splitext(file_path)
    if ext.lower() in no_rename_extensions:
        return False
    return True

"""
Reviews a code file and provides a brief summary of its functionality.

This function reads the content of a code file and uses a GPT-3.5 model to generate a review that summarizes
the code's functionality.

Args:
    file_path (str): The path to the code file to be reviewed.

Returns:
    str: A brief summary of the code's functionality as provided by the GPT model.
        If an error occurs, a fallback message ("Unable to review the file") is returned.

Raises:
    Exception: Catches and logs any errors that occur during the code review process.
"""
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

"""
Checks if a file is older than a specified threshold in days.

This function compares the current time with the file's last modification time 
to determine if the file is older than the given number of days.

Args:
    file_path (str): The path to the file being checked.
    days_threshold (int, optional): The age threshold in days. Defaults to 365 days.

Returns:
    bool: Returns True if the file is older than the specified number of days, False otherwise.
"""
def is_file_old(file_path, days_threshold=365):
    current_time = datetime.now().timestamp()
    last_access_time = os.path.getmtime(file_path)
    return (current_time - last_access_time) > (days_threshold * 24 * 60 * 60)

"""
Analyzes a file's content to determine if it is considered useless.

This function examines the content of a file to decide if it contains information that is deemed useless, 
such as non-English text, junk data, or installers. It uses a GPT-3.5 model to analyze the content and 
respond with either 'YES' (if the content is useless) or 'NO' (if the content might be valuable).

Args:
    file_path (str): The path to the file whose content needs to be analyzed.

Returns:
    bool: Returns True if the content is deemed useless ('YES' from the model), or False if the content is valuable 
        or can't be assessed (either 'NO' from the model or an error occurs).

Raises:
    Exception: Catches and logs any errors that occur during content analysis.
"""
def is_content_useless(file_path):
    content = get_file_content(file_path)
    if not content:
        return False

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

"""
Organizes files in a directory.

This function traverses the specified directory and performs several operations on the files:
- Removes old and potentially useless files.
- Deletes duplicates based on file hash.
- Removes specific file types (e.g., .dmg files).
- Organizes files into categories based on their type and content.
- Renames files based on their content, if necessary.
- Moves files into appropriate category folders.

Args:
    directory (str): The path to the directory that needs to be organized.
    user_categories (dict): A dictionary defining user-specific file categories and their associated types (e.g., extensions or MIME types).

Returns:
    None: The function modifies the file system by deleting, moving, and renaming files as needed.

Raises:
    Exception: Catches and logs any errors that occur during the file organization process.
"""
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

"""
Deletes empty folders within a specified directory.

This function walks through a directory and its subdirectories, checking each folder to see if it is empty.
If a folder is found to be empty, it is removed. Any errors encountered during the deletion process are logged.

Args:
    path (str): The path to the directory where empty folders should be deleted.

Returns:
    None: The function does not return any value. It simply performs the deletion of empty folders and prints logs.
"""
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
    
    use_custom_categories = input("Do you want to use a custom directory organization scheme? (y/n): ").lower() == 'y'
    
    categorization_scheme = {}
    if use_custom_categories:
        user_description = input("Describe how you'd like your files organized (e.g., 'I want my photos, documents, and code files separated'): ")
        categorization_scheme = get_ai_categorization_scheme(user_description)
        print("Generated categorization scheme:", categorization_scheme)
    
    organize_directory(target_directory, categorization_scheme)
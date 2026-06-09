import os
import re

def natural_sort_key(s):
    """Sort strings containing numbers in human/natural order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def get_html_files(directory):
    """Lists and naturally sorts HTML files in a given directory."""
    if not os.path.exists(directory):
        return []
    
    files = [
        f for f in os.listdir(directory) 
        if f.lower().endswith(('.html', '.xhtml', '.htm'))
    ]
    files.sort(key=natural_sort_key)
    return files

def read_file_content(file_path):
    """Reads text content from a file using UTF-8 encoding."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def ensure_directory_exists(directory):
    """Creates a directory if it does not already exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_txt_files(directory):
    """Lists and naturally sorts TXT files in a given directory."""
    if not os.path.exists(directory):
        return []

    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith('.txt')
    ]
    files.sort(key=natural_sort_key)
    return files

def get_next_output_path(outputs_dir, base_name="combined_text", extension=".txt"):
    """Determines the next non-conflicting output file path in the outputs directory."""
    ensure_directory_exists(outputs_dir)
    
    # Check baseline: combined_text.txt
    target_path = os.path.join(outputs_dir, f"{base_name}{extension}")
    if not os.path.exists(target_path):
        return target_path
    
    # Try combined_text_2.txt, combined_text_3.txt...
    counter = 2
    while True:
        target_path = os.path.join(outputs_dir, f"{base_name}_{counter}{extension}")
        if not os.path.exists(target_path):
            return target_path
        counter += 1

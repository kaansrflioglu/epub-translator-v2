import os
from src.parser import strip_tags
from src.file_handler import (
    get_html_files, 
    read_file_content, 
    get_next_output_path,
    ensure_directory_exists
)

def merge_broken_lines(text):
    """Detects and merges sentences that were incorrectly wrapped to the next line."""
    lines = text.splitlines()
    if not lines:
        return text
    
    sentence_enders = {'.', '!', '?', ':', '"', '”', '’', '-', '—', '*'}
    merged_lines = []
    
    i = 0
    while i < len(lines):
        current_line = lines[i].strip()
        
        # Last line check
        if i == len(lines) - 1:
            if current_line or (merged_lines and merged_lines[-1] != ""):
                merged_lines.append(current_line)
            i += 1
            continue
            
        next_line = lines[i+1].strip()
        
        # Check conditions for merging
        if current_line and next_line:
            last_char = current_line[-1]
            first_char = next_line[0]
            
            not_ended = last_char not in sentence_enders
            starts_lowercase = first_char.islower()
            ends_with_word_char = last_char.isalnum() or last_char in {',', ';'}
            
            if not_ended and starts_lowercase and ends_with_word_char:
                # Merge current line and next line, update next line for recursive checks
                lines[i+1] = current_line + " " + next_line
                i += 1
                continue
        
        # Handle regular line insertion with empty line control
        if current_line or (merged_lines and merged_lines[-1] != ""):
            merged_lines.append(current_line)
        i += 1
        
    return '\n'.join(merged_lines)

def process_single_file(file_path):
    """Reads, strips tags from, and cleans the text of a single HTML file."""
    html_content = read_file_content(file_path)
    cleaned_text = strip_tags(html_content).strip()
    return merge_broken_lines(cleaned_text)

def orchestrate_extraction(source_dir, outputs_dir, progress_callback=None):
    """
    Orchestrates the process of listing files, extracting and cleaning text,
    and saving to the next available unique file name inside the outputs directory.
    """
    # Verify or create folders
    ensure_directory_exists(source_dir)
    ensure_directory_exists(outputs_dir)
    
    # Get HTML files
    files = get_html_files(source_dir)
    if not files:
        return None, 0, []

    # Get output path
    output_path = get_next_output_path(outputs_dir)
    total_extracted_chars = 0
    processed_files = []

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for index, file_name in enumerate(files):
            file_path = os.path.join(source_dir, file_name)
            if progress_callback:
                progress_callback(index + 1, len(files), file_name)
            
            try:
                cleaned_text = process_single_file(file_path)
                
                # Write a page break separator if it is not the first file
                if index > 0:
                    outfile.write("\n\n---\n\n")
                outfile.write(cleaned_text)
                
                total_extracted_chars += len(cleaned_text)
                processed_files.append(file_name)
            except Exception as e:
                if progress_callback:
                    progress_callback(index + 1, len(files), f"ERROR {file_name}: {str(e)}")

    return output_path, total_extracted_chars, processed_files

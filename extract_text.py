import os
import sys

# Add root folder to sys.path just in case to avoid import errors in some environments
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.processor import orchestrate_extraction

def progress_logger(current, total, file_name):
    """Callback function to print progress logs during extraction."""
    print(f"[{current}/{total}] Processing: {file_name}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(current_dir, "html_source")
    outputs_dir = os.path.join(current_dir, "outputs")

    # Check if html_source folder exists or is empty before orchestrating
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"Created source folder: {source_dir}")
        print("Please place your HTML files in this folder and run the script again.")
        return

    print(f"Scanning for HTML files in: {source_dir}")
    
    # Run the orchestrator
    output_path, total_chars, processed_files = orchestrate_extraction(
        source_dir=source_dir,
        outputs_dir=outputs_dir,
        progress_callback=progress_logger
    )

    if not processed_files:
        print(f"\nNo HTML files found in 'html_source'.")
        print("Please place your HTML files in this folder and run the script again.")
        return

    print(f"\nSuccess! All text has been extracted and saved to:")
    print(f"--> {output_path}")
    print(f"Total processed files: {len(processed_files)}")
    print(f"Total characters written: {total_chars}")

if __name__ == "__main__":
    main()

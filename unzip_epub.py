import os
import sys

# Ensure root folder is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.file_handler import extract_epub_html, ensure_directory_exists

def get_epub_files(directory):
    """Lists and naturally sorts EPUB files in a given directory."""
    if not os.path.exists(directory):
        return []
    
    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith('.epub')
    ]
    # Simple sort is fine, or natural sort
    files.sort()
    return files

def pick_epub_file(epub_files: list[str]) -> str | None:
    """Prompts the user to pick one EPUB file from the list."""
    print("\nAvailable EPUB files in 'inputs/':\n")
    for i, name in enumerate(epub_files, start=1):
        print(f"  [{i}] {name}")

    while True:
        raw = input("\nEnter file number (or 'q' to quit): ").strip()
        if raw.lower() == "q":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(epub_files):
            return epub_files[int(raw) - 1]
        print("  Invalid input — please enter a number from the list.")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    inputs_dir = os.path.join(current_dir, "inputs")
    source_dir = os.path.join(current_dir, "html_source")

    # Ensure inputs directory exists
    ensure_directory_exists(inputs_dir)
    ensure_directory_exists(source_dir)

    # Scan for EPUB files
    epub_files = get_epub_files(inputs_dir)

    if not epub_files:
        print("\nNo EPUB files found in 'inputs/' folder.")
        print("Please place your EPUB files in 'inputs/' and run the script again.")
        return

    # --- EPUB Selection ---
    chosen_epub = pick_epub_file(epub_files)
    if not chosen_epub:
        print("Cancelled.")
        return

    epub_path = os.path.join(inputs_dir, chosen_epub)

    # --- Clear Target Directory Check ---
    clear_target = True
    existing_files = [f for f in os.listdir(source_dir) if not f.startswith('.')]
    if existing_files:
        print(f"\nCleaning 'html_source/' folder ({len(existing_files)} files) before extraction...")

    # --- Extract ---
    print(f"\nExtracting HTML/XHTML pages from: {chosen_epub}")
    try:
        extracted = extract_epub_html(epub_path, source_dir, clear_target=clear_target)
        
        if not extracted:
            print("\nNo HTML/XHTML pages found inside the selected EPUB.")
            return

        print(f"\nSuccess! Extracted {len(extracted)} files to 'html_source/' in spine/reading order.")
        print(f"First page: {extracted[0]}")
        print(f"Last page : {extracted[-1]}")
        print("\nNext step: Run 'python extract_text.py' to extract and merge text into a single TXT file.")
    except Exception as e:
        print(f"\nAn error occurred during extraction: {e}")

if __name__ == "__main__":
    main()

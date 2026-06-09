import os
import re

def detect_broken_lines(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    suspects = []
    
    # Common sentence-ending punctuation or symbols
    sentence_enders = {'.', '!', '?', ':', '"', '”', '’', '-', '—', '*'}
    
    for i in range(len(lines) - 1):
        current_line = lines[i].strip()
        next_line = lines[i+1].strip()
        
        # Skip empty lines, separators, and headings (often capitalized)
        if not current_line or not next_line:
            continue
        if current_line.startswith('---') or next_line.startswith('---'):
            continue
            
        # Condition 1: Current line does NOT end with sentence-ending punctuation
        last_char = current_line[-1] if current_line else ''
        not_ended = last_char not in sentence_enders
        
        # Condition 2: Next line starts with a lowercase letter
        first_char = next_line[0] if next_line else ''
        starts_lowercase = first_char.islower()
        
        # Condition 3: Check if the current line ends with a lowercase letter or comma/word char
        ends_with_word_char = last_char.isalnum() or last_char in {',', ';'}
        
        if not_ended and starts_lowercase and ends_with_word_char:
            suspects.append({
                'line_num': i + 1,
                'current': current_line,
                'next_num': i + 2,
                'next': next_line
            })

    print(f"Total lines analyzed: {len(lines)}")
    print(f"Suspected broken sentences found: {len(suspects)}\n")
    
    for idx, s in enumerate(suspects[:30], 1): # Show first 30
        print(f"Suspect #{idx} (Lines {s['line_num']}-{s['next_num']}):")
        print(f"  Line {s['line_num']}: {s['current']}")
        print(f"  Line {s['next_num']}: {s['next']}")
        print(f"  Merged Suggestion: {s['current']} {s['next']}\n")
        
    if len(suspects) > 30:
        print(f"... and {len(suspects) - 30} more suspects.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    combined_file = os.path.join(current_dir, "combined_text.txt")
    detect_broken_lines(combined_file)

import os
import sys

# Ensure project root is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.file_handler import get_txt_files, ensure_directory_exists
from src.translator import OllamaTranslator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pick_file(txt_files: list[str]) -> str | None:
    """Prompts the user to pick one TXT file from the list."""
    print("\nAvailable TXT files in 'outputs/':\n")
    for i, name in enumerate(txt_files, start=1):
        print(f"  [{i}] {name}")

    while True:
        raw = input("\nEnter file number (or 'q' to quit): ").strip()
        if raw.lower() == "q":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(txt_files):
            return txt_files[int(raw) - 1]
        print("  Invalid input — please enter a number from the list.")


def ask_target_language() -> str:
    raw = input("Target language [default: English]: ").strip()
    return raw if raw else "English"


def ask_model() -> str:
    raw = input("Ollama model to use [default: llama3]: ").strip()
    return raw if raw else "llama3"


def build_output_path(outputs_dir: str, source_name: str, target_lang: str) -> str:
    """
    Derives the output file path for a translation.

    Example:
        combined_text.txt  →  combined_text_translated_english.txt
    """
    base, _ = os.path.splitext(source_name)
    lang_slug = target_lang.lower().replace(" ", "_")
    filename = f"{base}_translated_{lang_slug}.txt"
    return os.path.join(outputs_dir, filename)


def progress_logger(current: int, total: int, preview: str):
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"\r  [{bar}] {current}/{total}  {preview[:50]:<50}", end="", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(current_dir, "outputs")

    ensure_directory_exists(outputs_dir)
    txt_files = get_txt_files(outputs_dir)

    if not txt_files:
        print("No TXT files found in 'outputs/'. Run extract_text.py first.")
        return

    # --- File selection ---
    chosen_name = pick_file(txt_files)
    if not chosen_name:
        print("Cancelled.")
        return

    input_path = os.path.join(outputs_dir, chosen_name)

    # --- Options ---
    target_lang = ask_target_language()
    model = ask_model()
    output_path = build_output_path(outputs_dir, chosen_name, target_lang)

    if os.path.exists(output_path):
        overwrite = input(f"\n'{os.path.basename(output_path)}' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            print("Cancelled.")
            return

    # --- Translate ---
    print(f"\nStarting translation -> {target_lang}  (model: {model})")
    print(f"Input  : {input_path}")
    print(f"Output : {output_path}\n")

    translator = OllamaTranslator(model=model)

    try:
        total_chars = translator.translate_file(
            input_path=input_path,
            output_path=output_path,
            target_lang=target_lang,
            progress_callback=progress_logger,
        )
    except KeyboardInterrupt as ki:
        print(f"\n\nWARNING: Translation interrupted. Completed parts saved:")
        print(f"  --> {output_path}")
        return
    except Exception as exc:
        print(f"\n\nError: {exc}")
        print("\nTroubleshooting:")
        print("  - Make sure Ollama is running:  ollama serve")
        print(f"  - Make sure the model is downloaded:   ollama pull {model}")
        print("  - Check that port 11434 is accessible.")
        return

    print(f"\n\nDone! {total_chars:,} characters written to:")
    print(f"  --> {output_path}")


if __name__ == "__main__":
    main()

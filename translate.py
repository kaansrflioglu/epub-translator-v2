import json
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


def ask_model(default_model: str = "llama3") -> str:
    raw = input(f"Ollama model to use [default: {default_model}]: ").strip()
    return raw if raw else default_model


def ask_genre(prompt_templates: dict, default_genre: str = "fiction") -> str:
    """Prompts the user to pick a book genre for optimized translation prompts."""
    if not prompt_templates:
        return default_genre

    genre_keys = list(prompt_templates.keys())
    default_key = default_genre if default_genre in prompt_templates else genre_keys[0]
    default_label = prompt_templates[default_key]["label"]

    print("\nSelect book genre for optimized translation:\n")
    for i, key in enumerate(genre_keys, start=1):
        g = prompt_templates[key]
        marker = " (default)" if key == default_key else ""
        print(f"  [{i}] {g['label']}{marker}")
        print(f"      {g['description']}")

    while True:
        raw = input(f"\nGenre number [default: {default_label}]: ").strip()
        if not raw:
            return default_key
        if raw.isdigit() and 1 <= int(raw) <= len(genre_keys):
            selected = genre_keys[int(raw) - 1]
            print(f"  Using prompt template: {prompt_templates[selected]['label']}")
            return selected
        print("  Invalid input — please enter a number from the list.")


def build_output_path(outputs_dir: str, source_name: str, target_lang: str) -> str:
    """
    Derives the output file path for a translation.

    Example:
        combined_text.txt  ->  combined_text_translated_english.txt
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

    # Exclude already-translated output files so the user only picks source files
    txt_files = [f for f in txt_files if "_translated_" not in f]

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

    # Load config once to get model default and genre list
    config = {}
    config_path = os.path.join(current_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    default_model = config.get("ollama", {}).get("model", "llama3")
    model = ask_model(default_model)

    prompt_templates = config.get("prompt_templates", {})
    default_genre = config.get("default_genre", "fiction")
    genre = ask_genre(prompt_templates, default_genre)

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

    translator = OllamaTranslator(model=model, genre=genre)

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

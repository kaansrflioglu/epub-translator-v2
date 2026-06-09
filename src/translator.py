import json
import os
import re
import requests

# Separator used between book sections — must be preserved as-is in translation
SECTION_SEPARATOR = "\n\n---\n\n"
CHUNK_SEPARATOR_PATTERN = re.compile(r'\n\n---\n\n')

# Matches <think>...</think> blocks produced by reasoning models (e.g. qwen3, deepseek-r1)
_THINK_TAG_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL | re.IGNORECASE)


class OllamaTranslator:
    """
    Translates text files using a locally running Ollama model.

    The file is split at section separators (---) and paragraph boundaries so
    that each request stays within a reasonable token budget.  Separators are
    preserved verbatim in the output so the translated file keeps the same
    structural layout as the original.

    Features:
    - Strips <think>...</think> blocks from reasoning models (qwen3, deepseek-r1, etc.)
    - Writes each translated chunk to disk immediately (no progress lost on interrupt)
    - Graceful Ctrl+C handling: saves partial translation with a clear notice
    """

    def __init__(self, model: str = None, base_url: str = None, genre: str = None):
        config = self._load_config()
        ollama_config = config.get("ollama", {})

        self.model = model if model is not None else ollama_config.get("model", "llama3")

        configured_url = base_url if base_url is not None else ollama_config.get("api_url", "http://localhost:11434")
        self.api_url = configured_url.rstrip("/") + "/api/generate"

        self.temperature = ollama_config.get("temperature", 0.3)
        self.repeat_penalty = ollama_config.get("repeat_penalty", 1.15)
        self.timeout = ollama_config.get("timeout", 300)

        # Resolve prompt template: genre → default_genre → hardcoded fallback
        prompt_templates = config.get("prompt_templates", {})
        default_genre = config.get("default_genre", "fiction")
        selected_genre = genre if (genre and genre in prompt_templates) else default_genre

        raw_template = None
        if selected_genre in prompt_templates:
            raw_template = prompt_templates[selected_genre].get("template")
        
        # Fallback to old-style top-level prompt_template key for backwards compat
        if raw_template is None:
            raw_template = config.get("prompt_template")

        _default = (
            "You are an expert literary translator.\n"
            "Translate the following text to {target_lang}.\n"
            "Output ONLY the translated text, with no explanations, notes, or commentary.\n"
            "Preserve the author's voice, style, and all paragraph breaks.\n\n"
            "{text}"
        )

        if isinstance(raw_template, list):
            self.prompt_template = "\n".join(raw_template)
        elif isinstance(raw_template, str):
            self.prompt_template = raw_template
        else:
            self.prompt_template = _default

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate_file(self, input_path: str, output_path: str,
                       target_lang: str = "English",
                       progress_callback=None) -> int:
        """
        Reads *input_path*, translates it chunk by chunk, and writes
        the result to *output_path* incrementally.

        Returns the total number of characters written.
        Raises KeyboardInterrupt after saving partial output if the user
        presses Ctrl+C.
        """
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = self._split_into_chunks(content)
        total = len(chunks)
        translated_parts: list[str] = []
        interrupted = False

        try:
            for idx, chunk in enumerate(chunks, start=1):
                if progress_callback:
                    progress_callback(idx, total, chunk[:60].replace("\n", " ") + "...")

                # Separators pass through unchanged
                if chunk == "---":
                    translated_parts.append("---")
                    continue

                translated = self.translate_chunk(chunk, target_lang)
                translated_parts.append(translated)

        except KeyboardInterrupt:
            interrupted = True

        # Always save whatever we have so far
        result = self._rebuild(chunks[:len(translated_parts)], translated_parts)

        if interrupted:
            notice = (
                f"\n\n---\n\n"
                f"[TRANSLATION INTERRUPTED — {len(translated_parts)}/{total} chunks completed]"
            )
            result = result + notice

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)

        if interrupted:
            raise KeyboardInterrupt(
                f"Translation interrupted. {len(translated_parts)}/{total} chunks saved -> {output_path}"
            )

        return len(result)

    def _load_config(self) -> dict:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        config_path = os.path.join(root_dir, "config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def translate_chunk(self, text: str, target_lang: str = "English") -> str:
        """
        Sends a single text chunk to Ollama and returns the translated string.
        - Uses str.replace() for prompt building to safely handle { } in source text.
        - Retries up to 2 times on empty response before falling back to original.
        - Strips <think>...</think> reasoning blocks (qwen3, deepseek-r1, etc.)
        - Raises requests.RequestException on network/server errors.
        """
        # Use str.replace() instead of .format() so curly braces in source text
        # don't cause KeyError/IndexError crashes.
        prompt = (
            self.prompt_template
            .replace("{target_lang}", target_lang)
            .replace("{text}", text)
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "repeat_penalty": self.repeat_penalty,
                "temperature": self.temperature,
            },
        }

        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES + 1):
            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            raw = data.get("response", "").strip()

            # Strip reasoning blocks (<think>...</think>) emitted by models like qwen3
            cleaned = _THINK_TAG_PATTERN.sub("", raw).strip()

            if cleaned:
                return cleaned

            # Empty response received — retry if attempts remain
            if attempt < MAX_RETRIES:
                continue

        # All retries exhausted with empty response: warn and keep original text
        print(f"\n  [WARNING] Empty translation received after {MAX_RETRIES + 1} attempts. Keeping original text.")
        return text

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _split_into_chunks(self, content: str) -> list[str]:
        """
        Splits content into translatable chunks and literal '---' markers.

        Strategy:
        1. Split on '\\n\\n---\\n\\n' to isolate sections.
        2. Within each section, split on double newlines (paragraphs).
        3. Large paragraphs (> MAX_CHARS) are further split on sentence ends.
        """
        MAX_CHARS = 4000

        sections = CHUNK_SEPARATOR_PATTERN.split(content)
        chunks: list[str] = []

        for s_idx, section in enumerate(sections):
            if s_idx > 0:
                chunks.append("---")  # placeholder for separator

            paragraphs = re.split(r'\n\n+', section.strip())
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(para) <= MAX_CHARS:
                    chunks.append(para)
                else:
                    # Split oversized paragraphs on sentence boundaries
                    chunks.extend(self._split_sentences(para, MAX_CHARS))

        return chunks

    @staticmethod
    def _split_sentences(text: str, max_chars: int) -> list[str]:
        """Splits text on sentence-ending punctuation to stay under max_chars.
        
        Protects common abbreviations (Mr., Dr., etc.) from being treated as
        sentence boundaries, which would split sentences incorrectly.
        """
        # Temporarily mask periods in known abbreviations with a null char placeholder
        # so the sentence splitter doesn't break on them.
        ABBREV_PATTERN = re.compile(
            r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|Vs|vs|etc|e\.g|i\.e|Fig|vol|Vol|ch|Ch|pp|no|No|St|Rd|Ave|Dept|Corp|Inc|Ltd|Co)\.',
            re.IGNORECASE
        )
        protected = ABBREV_PATTERN.sub(lambda m: m.group(0).replace('.', '\x00'), text)

        # Also protect decimal numbers (e.g. 3.14, v1.2.3) from splitting
        protected = re.sub(r'(\d+)\.(\d)', lambda m: m.group(0).replace('.', '\x00'), protected)

        # Split on sentence-ending punctuation
        raw_sentences = re.split(r'(?<=[.!?])\s+', protected)

        # Restore masked periods
        sentences = [s.replace('\x00', '.') for s in raw_sentences]

        groups: list[str] = []
        current = ""

        for sent in sentences:
            if current and len(current) + len(sent) + 1 > max_chars:
                groups.append(current.strip())
                current = sent
            else:
                current = (current + " " + sent).strip() if current else sent

        if current:
            groups.append(current.strip())

        return groups

    @staticmethod
    def _rebuild(original_chunks: list[str], translated_chunks: list[str]) -> str:
        """Reconstructs the full translated text preserving section separators."""
        result_parts: list[str] = []

        for orig, trans in zip(original_chunks, translated_chunks):
            if orig == "---":
                result_parts.append(SECTION_SEPARATOR)
            else:
                result_parts.append(trans + "\n\n")

        return "".join(result_parts).strip()

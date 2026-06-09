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

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = base_url.rstrip("/") + "/api/generate"

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
                    progress_callback(idx, total, chunk[:60].replace("\n", " ") + "…")

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

    def translate_chunk(self, text: str, target_lang: str = "English") -> str:
        """
        Sends a single text chunk to Ollama and returns the translated string.
        - Strips <think>...</think> reasoning blocks (qwen3, deepseek-r1, etc.)
        - Raises requests.RequestException on network/server errors.
        """
        prompt = (
            f"Translate the following text to {target_lang}. "
            "Output ONLY the translated text, with no explanations, notes, prefixes, or commentary. "
            f"Use natural, grammatically correct {target_lang}. "
            "Do NOT repeat any word or phrase.\n\n"
            f"{text}"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "repeat_penalty": 1.15,
                "temperature": 0.3,
            },
        }

        response = requests.post(self.api_url, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "").strip()

        # Strip reasoning blocks (<think>…</think>) emitted by models like qwen3
        cleaned = _THINK_TAG_PATTERN.sub("", raw).strip()
        return cleaned

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
        """Splits text on sentence-ending punctuation to stay under max_chars."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
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

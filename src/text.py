import re
import unicodedata

NON_WHITESPACE_RE = re.compile(r"\S+")
ASCII_REPLACEMENTS = str.maketrans(
    {
        "—": "-",
        "–": "-",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "…": "...",
    }
)


def _repair_mojibake_word(match: re.Match[str]) -> str:
    word = match.group(0)
    try:
        return word.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return word


def ascii_message(message: str) -> str:
    """Repair common UTF-8 mojibake and convert outgoing text to ASCII."""
    repaired = NON_WHITESPACE_RE.sub(_repair_mojibake_word, str(message))
    replaced = repaired.translate(ASCII_REPLACEMENTS)
    return unicodedata.normalize("NFKD", replaced).encode("ascii", "ignore").decode("ascii")

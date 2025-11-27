import hashlib
import re
from typing import List

def normalize_code(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def file_fingerprint(text: str) -> str:
    return sha256(normalize_code(text))

def extract_distinct_lines(text: str, k: int = 3) -> List[str]:
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
            continue
        if len(s) < 20:
            continue
        lines.append(s)
        if len(lines) >= k:
            break
    return lines

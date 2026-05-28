import os
import re
from pathlib import Path


def get_project_files(folder_path: str) -> dict[str, str]:
    """Read all text files in the project folder."""
    files = {}
    folder = Path(folder_path)
    if not folder.exists():
        return files

    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env", "dist", "build"}
    skip_exts = {".pyc", ".pyo", ".so", ".o", ".a", ".lib", ".dll", ".exe", ".bin",
                 ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg", ".mp3", ".mp4",
                 ".zip", ".tar", ".gz", ".pdf"}

    for path in folder.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix not in skip_exts:
            try:
                relative = str(path.relative_to(folder))
                files[relative] = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
    return files


def build_context(folder_path: str) -> str:
    """Build a context string from all project files."""
    files = get_project_files(folder_path)
    if not files:
        return ""

    parts = ["Current project files:"]
    for filename, content in files.items():
        parts.append(f"\n--- {filename} ---\n{content}")
    return "\n".join(parts)


def parse_ai_response(response: str, folder_path: str) -> list[dict]:
    """
    Parse AI response and extract file operations.
    Looks for:
      FILE: path/to/file.py
      ```
      ...content...
      ```
    or MODIFY: path/to/file.py with a diff block.
    """
    operations = []

    # Match FILE: or MODIFY: blocks
    pattern = re.compile(
        r'(?:FILE|MODIFY|CREATE):\s*([^\n]+)\n```(?:\w+)?\n(.*?)```',
        re.DOTALL | re.IGNORECASE
    )

    for match in pattern.finditer(response):
        filepath = match.group(1).strip()
        content = match.group(2)
        operations.append({"path": filepath, "content": content})

    return operations


def write_files(operations: list[dict], folder_path: str) -> list[str]:
    """Write or overwrite files from parsed operations."""
    written = []
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)

    for op in operations:
        target = folder / op["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(op["content"], encoding="utf-8")
        written.append(op["path"])

    return written


def build_generation_prompt(user_prompt: str, folder_path: str) -> str:
    """Build a prompt that includes project context and instructions for file output."""
    context = build_context(folder_path)

    instructions = """You are a code generation assistant. When creating or modifying files, always use this exact format:

FILE: path/to/filename.ext
```language
...full file content...
```

Rules:
- Always output the COMPLETE file content, never partial snippets.
- If a file already exists in the project context, modify it in place — do not create a new file.
- If adding to an existing file, include ALL original content plus your additions.
- Use the FILE: format for every file you create or modify.
- You can create multiple files in one response.
"""

    if context:
        return f"{instructions}\n\n{context}\n\nUser request: {user_prompt}"
    else:
        return f"{instructions}\n\nUser request: {user_prompt}"

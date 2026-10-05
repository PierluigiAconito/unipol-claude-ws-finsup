#!/usr/bin/env python
"""Hook PostToolUse: blocca scritture che violano il vincolo "niente consigli
finanziari" del Tema 02, applicando app/content_guard.py anche in fase di
scrittura/modifica dei file, non solo a runtime nell'app.

Riceve su stdin il payload JSON dell'hook di Claude Code (tool_name,
tool_input, ...). Exit code 2 = blocca e mostra il messaggio a Claude Code.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    from app.content_guard import find_violations
except ImportError:
    find_violations = None

# File che contengono le frasi vietate di proposito (pattern di rilevamento,
# fixture di test): vanno esclusi dalla scansione per evitare falsi positivi.
EXCLUDED_SUFFIXES = ("content_guard.py", "test_content_guard.py")
EXCLUDED_DIRS = (".claude/",)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = payload.get("tool_input", {})
    file_path = (tool_input.get("file_path") or "").replace("\\", "/")
    content = tool_input.get("content") or tool_input.get("new_string") or ""

    if not content or find_violations is None:
        return 0
    if file_path.endswith(EXCLUDED_SUFFIXES) or any(d in file_path for d in EXCLUDED_DIRS):
        return 0

    violations = find_violations(content)
    if violations:
        print(
            f"Blocco: il testo scritto in {file_path} contiene linguaggio da "
            f"consulenza finanziaria vietato dal Tema 02 -> {violations}. "
            "Riformula come spiegazione, non come consiglio d'azione.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

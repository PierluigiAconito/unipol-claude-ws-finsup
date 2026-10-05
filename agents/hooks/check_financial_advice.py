#!/usr/bin/env python
"""Hook PreToolUse: blocca le scritture che violano il vincolo "niente consigli
finanziari" del Tema 02, applicando lo stesso guardrail dell'app
(app/finsup/content_guard.py) anche in fase di sviluppo, non solo a runtime.

PreToolUse (non PostToolUse): con exit code 2 la Write/Edit non avviene
proprio e il motivo torna a Claude Code, che deve riformulare. Un hook
PostToolUse scatterebbe a file gia' scritto.

Riceve su stdin il payload JSON dell'hook (tool_name, tool_input, ...).
Fail-open: se il guardrail non e' importabile o il payload non e'
interpretabile, lascia passare (un hook rotto non deve bloccare il team).
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app"))

try:
    from finsup.content_guard import find_violations
except ImportError:
    find_violations = None

# Percorsi che contengono le frasi vietate di proposito (pattern di
# rilevamento, fixture di test, casi d'esempio delle skill) o configurazione
# dell'harness: esclusi per evitare falsi positivi.
EXCLUDED_SUFFIXES = ("content_guard.py",)
EXCLUDED_DIRS = ("app/tests/", "agents/hooks/", "agents/skills/", ".claude/")


def _written_text(tool_input: dict) -> str:
    """Testo che lo strumento sta per scrivere (Write, Edit, MultiEdit)."""
    if tool_input.get("content"):
        return tool_input["content"]
    if tool_input.get("new_string"):
        return tool_input["new_string"]
    edits = tool_input.get("edits") or []
    return "\n".join(e.get("new_string", "") for e in edits if isinstance(e, dict))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = (tool_input.get("file_path") or "").replace("\\", "/")
    content = _written_text(tool_input)

    if not content or find_violations is None:
        return 0
    if file_path.endswith(EXCLUDED_SUFFIXES) or any(d in file_path for d in EXCLUDED_DIRS):
        return 0

    violations = find_violations(content)
    if violations:
        print(
            f"Blocco: il testo per {file_path} contiene linguaggio da "
            f"consulenza finanziaria vietato dal Tema 02 -> {violations}. "
            "Riformula come spiegazione, non come consiglio d'azione.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

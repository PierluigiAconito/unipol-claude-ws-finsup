"""Test dell'hook PreToolUse agents/hooks/check_financial_advice.py.

Lo eseguono come lo esegue Claude Code: payload JSON su stdin, esito
dall'exit code (2 = scrittura bloccata, 0 = consentita).
"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "agents" / "hooks" / "check_financial_advice.py"

ADVICE = "Ti consiglio di investire in questo fondo."
EXPLANATION = "Il TAEG indica il costo totale del prestito in percentuale annua."


def run_hook(payload) -> int:
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)], input=data, capture_output=True, text=True
    ).returncode


def test_blocks_write_with_advice():
    payload = {"tool_name": "Write", "tool_input": {"file_path": "app/main.py", "content": ADVICE}}
    assert run_hook(payload) == 2


def test_blocks_edit_with_advice():
    payload = {"tool_name": "Edit", "tool_input": {"file_path": "agents/prompts/x.md", "new_string": ADVICE}}
    assert run_hook(payload) == 2


def test_blocks_multiedit_with_advice():
    payload = {
        "tool_name": "MultiEdit",
        "tool_input": {"file_path": "app/main.py", "edits": [{"old_string": "a", "new_string": ADVICE}]},
    }
    assert run_hook(payload) == 2


def test_allows_educational_write():
    payload = {"tool_name": "Write", "tool_input": {"file_path": "app/main.py", "content": EXPLANATION}}
    assert run_hook(payload) == 0


def test_skips_excluded_paths():
    payload = {"tool_name": "Write", "tool_input": {"file_path": "app/tests/test_x.py", "content": ADVICE}}
    assert run_hook(payload) == 0


def test_fails_open_on_bad_payload():
    assert run_hook("non json") == 0

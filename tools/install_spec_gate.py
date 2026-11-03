"""Install a project-scoped Claude Code PreToolUse hook.

Run once on the computer where Claude Code operates:
    python tools/install_spec_gate.py --project C:\\ruta\\proyecto
The installer preserves unrelated .claude/settings.json fields and hooks.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

MARKER = "Write|Edit|MultiEdit|NotebookEdit|Bash|PowerShell"


def command_for(project, interpreter=None, hook_file=None):
    interpreter = str(Path(interpreter or sys.executable).resolve())
    hook_file = str(Path(hook_file or Path(__file__).with_name("spec_gate_hook.py")).resolve())
    args = [interpreter, hook_file, "--project", str(project.resolve())]
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)


def install(project, python_exe=None, hook_file=None):
    root = Path(project).resolve()
    if not root.is_dir():
        raise ValueError(f"no existe el proyecto: {root}")
    if not (root / "sdd.json").is_file():
        raise ValueError(f"falta {root / 'sdd.json'}; configure el proyecto antes de instalar el hook")
    settings_path = root / ".claude" / "settings.json"
    if settings_path.is_file():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        if not isinstance(settings, dict):
            raise ValueError("settings.json debe ser un objeto JSON")
    else:
        settings = {}
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("settings.json: hooks debe ser un objeto")
    pre = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre, list):
        raise ValueError("settings.json: hooks.PreToolUse debe ser lista")

    new_command = command_for(root, python_exe, hook_file)
    group = {
        "matcher": MARKER,
        "hooks": [{"type": "command", "command": new_command, "timeout": 15}],
    }
    # Replace only a previous installer-managed record for this exact project.
    # Do not erase other PreToolUse hooks.
    previous = [
        i for i, item in enumerate(pre)
        if isinstance(item, dict) and item.get("matcher") == MARKER
        and any(isinstance(h, dict) and "spec_gate_hook.py" in h.get("command", "")
                for h in item.get("hooks", []) if isinstance(item.get("hooks"), list))
    ]
    for index in reversed(previous):
        del pre[index]
    pre.append(group)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = settings_path.with_name("settings.json.tmp")
    tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(settings_path)
    return settings_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    try:
        path = install(args.project)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] Hook instalado en {path}; reinicie Claude Code para cargarlo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

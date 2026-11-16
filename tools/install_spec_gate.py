"""Install a project-scoped Claude Code PreToolUse hook.

Run once on the computer where Claude Code operates:
    python tools/install_spec_gate.py --project C:\\ruta\\proyecto
The installer preserves unrelated .claude/settings.json fields and hooks.
"""
import argparse
import json
import sys
from pathlib import Path

MARKER = "Write|Edit|NotebookEdit|Bash|PowerShell"
HOOK_NAME = "spec_gate_hook.py"


def _is_spec_gate(item):
    """True for a PreToolUse group managed by this installer (any older matcher)."""
    if not isinstance(item, dict) or not isinstance(item.get("hooks"), list):
        return False
    for hook in item["hooks"]:
        if not isinstance(hook, dict):
            continue
        args = hook.get("args")
        parts = [hook.get("command")] + (args if isinstance(args, list) else [])
        if any(isinstance(p, str) and HOOK_NAME in p for p in parts):
            return True
    return False


def command_for(project, interpreter=None, hook_file=None):
    interpreter = str(Path(interpreter or sys.executable).resolve())
    hook_file = str(Path(hook_file or Path(__file__).with_name("spec_gate_hook.py")).resolve())
    return interpreter, [hook_file, "--project", str(project.resolve())]


def install(project, python_exe=None, hook_file=None):
    root = Path(project).resolve()
    if not root.is_dir():
        raise ValueError(f"no existe el proyecto: {root}")
    if not (root / "sdd.json").is_file():
        raise ValueError(f"falta {root / 'sdd.json'}; configure el proyecto antes de instalar el hook")
    settings_path = root / ".claude" / "settings.local.json"
    if settings_path.is_file():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        if not isinstance(settings, dict):
            raise ValueError("settings.local.json debe ser un objeto JSON")
    else:
        settings = {}
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("settings.local.json: hooks debe ser un objeto")
    pre = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre, list):
        raise ValueError("settings.local.json: hooks.PreToolUse debe ser lista")

    executable, args = command_for(root, python_exe, hook_file)
    group = {
        "matcher": MARKER,
        "hooks": [{"type": "command", "command": executable, "args": args,
                   "timeout": 15, "onFailure": "block"}],
    }
    # Replace previous installer-managed records (including ones written with an
    # older matcher). Do not erase other PreToolUse hooks.
    pre[:] = [item for item in pre if not _is_spec_gate(item)]
    pre.append(group)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = settings_path.with_name("settings.local.json.tmp")
    tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(settings_path)
    return settings_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    try:
        path = install(args.project)
    except (ValueError, OSError) as exc:  # JSONDecodeError subclasses ValueError
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] Hook instalado en {path}; reinicie Claude Code para cargarlo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

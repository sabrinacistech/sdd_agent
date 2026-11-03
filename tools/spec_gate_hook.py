"""PreToolUse gate for a *target project* with sdd.json.

Usage (called by Claude Code): python spec_gate_hook.py --project <path>
The event is JSON on stdin. Exit 2 + stderr denies a tool operation.
A project hook is a workflow guard, NOT a security sandbox.
"""
import argparse
import json
import sys
from pathlib import Path

from project_policy import validate

FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
SUPPORTED = FILE_TOOLS | SHELL_TOOLS


def decide(project, event):
    """Return (allowed, explanation); deny if input is ambiguous or invalid."""
    root = Path(project).resolve()
    if not root.is_dir():
        return False, "La raiz del proyecto destino no existe."
    if not isinstance(event, dict):
        return False, "Evento PreToolUse invalido."
    name = event.get("tool_name")
    data = event.get("tool_input")
    if name not in SUPPORTED or not isinstance(data, dict):
        return False, "Herramienta no reconocida por el Spec Gate."
    # A pinned root prevents accidental use of the agent repo as target.
    if name in FILE_TOOLS:
        destination = data.get("file_path")
        if not isinstance(destination, str) or not destination.strip() or "\x00" in destination:
            return False, "Falta file_path valido."
        path = Path(destination)
        # Claude provides absolute file paths; relative paths use event cwd.
        if not path.is_absolute():
            cwd = event.get("cwd")
            if not isinstance(cwd, str) or not cwd.strip():
                return False, "Ruta relativa sin cwd verificable."
            path = Path(cwd) / path
        try:
            path = path.resolve()
            relative = path.relative_to(root)
        except (ValueError, OSError, RuntimeError):
            return False, "La operacion apunta fuera del proyecto SDD configurado."
        # Documentation and configuration can be edited to close the gate;
        # never exempt code/tools/hooks or paths outside the target project.
        if relative.parts and relative.parts[0] == "docs" and len(relative.parts) > 1:
            return True, ""
        if relative == Path("sdd.json"):
            return True, ""

    errors, _ = validate(root, "all")
    if errors:
        lines = "\n".join(" - " + x for x in errors[:12])
        extra = f"\n ... y {len(errors) - 12} errores mas" if len(errors) > 12 else ""
        return False, (
            "SPEC GATE: requisitos/diseno incompletos en el proyecto destino.\n"
            f"{lines}{extra}\n"
            "Completar documentos mediante Write/Edit y validar con "
            "python tools/project_policy.py --project <proyecto>. "
            "Los comandos Bash/PowerShell permanecen bloqueados mientras el gate este cerrado."
        )
    return True, ""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Raiz absoluta del proyecto destino")
    args = parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
        allowed, reason = decide(args.project, event)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        allowed, reason = False, f"SPEC GATE: evento invalido: {exc}"
    if allowed:
        return 0
    print(reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

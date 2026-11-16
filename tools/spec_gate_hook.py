"""PreToolUse gate for a *target project* with sdd.json.

Usage (called by Claude Code): python spec_gate_hook.py --project <path>
The event is JSON on stdin. Exit 2 + stderr denies a tool operation.
A project hook is a workflow guard, NOT a security sandbox.
"""
import argparse
import json
import sys
from pathlib import Path

from project_policy import spec_paths, validate

FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
SUPPORTED = FILE_TOOLS | SHELL_TOOLS


def is_spec_document(root, path):
    """True if path is a specification document Claude may edit to close the gate.

    Covers docs/, the documents and ADR directory declared in sdd.json, and Mermaid
    diagrams. sdd.json itself is NOT included: changing the policy while the gate
    is closed is a human decision.
    """
    relative = path.relative_to(root)
    if relative.parts and relative.parts[0] == "docs" and len(relative.parts) > 1:
        return True
    if path.suffix.lower() == ".mmd":
        return True
    try:
        files, dirs = spec_paths(root)
    except (ValueError, OSError):
        return False  # Invalid sdd.json: only docs/ remains editable.
    return path in files or any(path.is_relative_to(d) and path != d for d in dirs)


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
    path = None
    # A pinned root prevents accidental use of the agent repo as target.
    if name in FILE_TOOLS:
        destination = data.get("notebook_path") if name == "NotebookEdit" else data.get("file_path")
        if not isinstance(destination, str) or not destination.strip() or "\x00" in destination:
            return False, "Falta ruta de archivo valida."
        path = Path(destination)
        # Claude provides absolute file paths; relative paths use event cwd.
        if not path.is_absolute():
            cwd = event.get("cwd")
            if not isinstance(cwd, str) or not cwd.strip():
                return False, "Ruta relativa sin cwd verificable."
            path = Path(cwd) / path
        try:
            path = path.resolve()
            path.relative_to(root)
        except (ValueError, OSError, RuntimeError):
            return False, "La operacion apunta fuera del proyecto SDD configurado."
        # Specification documents can be edited to close the gate;
        # never exempt code/tools/hooks, sdd.json or paths outside the project.
        if is_spec_document(root, path):
            return True, ""

    errors, _ = validate(root, "all")
    if errors:
        lines = "\n".join(" - " + x for x in errors[:12])
        extra = f"\n ... y {len(errors) - 12} errores mas" if len(errors) > 12 else ""
        hint = ""
        if path is not None and path == root / "sdd.json":
            hint = ("\nsdd.json define la politica del gate: mientras este cerrado, "
                    "solo una persona responsable puede modificarlo fuera de Claude Code.")
        return False, (
            "SPEC GATE: requisitos/diseno incompletos en el proyecto destino.\n"
            f"{lines}{extra}\n"
            "Completar los documentos declarados en sdd.json mediante Write/Edit y validar con "
            "python tools/project_policy.py --project <proyecto>. "
            "Los comandos Bash/PowerShell permanecen bloqueados mientras el gate este cerrado."
            f"{hint}"
        )
    return True, ""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Raiz absoluta del proyecto destino")
    args = parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
        allowed, reason = decide(args.project, event)
    except (ValueError, OSError) as exc:  # JSONDecodeError subclasses ValueError
        allowed, reason = False, f"SPEC GATE: evento invalido: {exc}"
    if allowed:
        return 0
    print(reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

"""Hook PreToolUse: impide escribir codigo mientras la spec este incompleta.

Se dispara antes de Write/Edit. Deja pasar libremente la escritura de la propia
spec (docs/, tools/, .claude/, CLAUDE.md, README.md) para que se pueda completar
lo que falta; bloquea cualquier otro archivo si spec_lint encuentra errores.

Salida 2 = bloquear y devolverle el motivo al agente.
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

from spec_lint import run_checks  # noqa: E402

# Rutas que NO son codigo de producto: siempre se pueden editar.
EXENTAS = ("docs/", "tools/", ".claude/", ".git/")
ARCHIVOS_EXENTOS = ("claude.md", "readme.md", ".gitignore", ".gitattributes")


def exenta(ruta_abs):
    try:
        rel = os.path.relpath(ruta_abs, RAIZ).replace("\\", "/")
    except ValueError:
        # Otra unidad de disco: fuera del proyecto, no nos corresponde bloquear.
        return True
    if rel.startswith(".."):
        return True
    if os.path.basename(rel).lower() in ARCHIVOS_EXENTOS:
        return True
    return any(rel.startswith(p) for p in EXENTAS)


def main():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # Ante un payload que no entendemos, no bloqueamos.

    destino = (evento.get("tool_input") or {}).get("file_path")
    if not destino or exenta(os.path.abspath(destino)):
        return 0

    errores, _ = run_checks(RAIZ, "all")
    if not errores:
        return 0

    detalle = "\n".join(f"  - {e}" for e in errores[:10])
    sobrantes = len(errores) - 10
    if sobrantes > 0:
        detalle += f"\n  ... y {sobrantes} error(es) mas."

    print(
        "SPEC GATE: no se puede implementar todavia.\n"
        f"La spec de Requisitos/Diseno esta incompleta ({len(errores)} error(es)):\n"
        f"{detalle}\n\n"
        "Completa docs/01-requisitos/ y docs/02-diseno/ antes de escribir codigo. "
        "Verifica con: python tools/spec_lint.py",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())

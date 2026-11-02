"""Reusable SDD project validator. Python standard library only.

Usage: python tools/project_policy.py --project /path/to/target [--stage 1|2|all]
The target project owns sdd.json and its documents. The agent repository does not.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from profile_rules import validate_profiles, load_profiles

DEFAULTS = {
    "schema_version": 1,
    "profile": "generic",
    "profiles": [],
    "documents": {
        "requirements": "docs/01-requisitos/PRD.md",
        "architecture": "docs/02-diseno/arquitectura.md",
        "guardrails": "docs/02-diseno/guardrails.md",
        "adr_directory": "docs/02-diseno/adr",
    },
    "requirements_sections": [
        "Problema y objetivo", "Usuarios y actores", "Alcance",
        "Requisitos funcionales", "Requisitos no funcionales",
        "Dependencias", "Criterios de aceptacion", "Decisiones pendientes",
    ],
    "architecture_sections": [
        "Vista general", "Componentes", "Stack y librerias",
        "Patrones de arquitectura", "Seguridad", "Restricciones tecnicas", "Diagramas",
    ],
}
PLACEHOLDER = re.compile(r"\b(?:TBD|TODO|FIXME|PENDIENTE|COMPLETAR)\b|<(?:por definir|completar|pendiente)>", re.I)
ADR_REF = re.compile(r"ADR-(\d{4})", re.I)
HEADING = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.M)


def normalize(text):
    return " ".join(text.casefold().translate(str.maketrans("áéíóúüñ", "aeiouun")).split())


def resolve_within(root, value):
    """Reject absolute paths and traversal in project configuration or references."""
    path = Path(value)
    if path.is_absolute() or not value or "\x00" in value:
        raise ValueError(f"ruta invalida: {value!r}")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"ruta fuera del proyecto: {value!r}")
    return resolved


def configuration(root):
    config_file = root / "sdd.json"
    if not config_file.is_file():
        raise ValueError("falta sdd.json en el proyecto (ver examples/generic/sdd.json)")
    config = json.loads(config_file.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("sdd.json: schema_version debe ser 1")
    # Legacy "profile" remains supported for backward compatibility.
    legacy = config.get("profile", "generic")
    if legacy != "generic" and "profiles" not in config:
        config["profiles"] = [legacy]
    load_profiles(config.get("profiles", []))
    settings = {**DEFAULTS, **config}
    settings["documents"] = {**DEFAULTS["documents"], **config.get("documents", {})}
    for key, value in settings["documents"].items():
        if not isinstance(value, str):
            raise ValueError(f"documents.{key} debe ser texto")
        resolve_within(root, value)
    for key in ("requirements_sections", "architecture_sections"):
        if not isinstance(settings[key], list) or not settings[key] or not all(isinstance(s, str) and s.strip() for s in settings[key]):
            raise ValueError(f"{key} debe ser lista no vacia de titulos")
    return settings


def read_doc(root, rel, errors):
    path = resolve_within(root, rel)
    if not path.is_file():
        errors.append(f"{rel}: no existe")
        return None
    return path.read_text(encoding="utf-8")


def sections(text):
    matches = list(HEADING.finditer(text))
    return {normalize(m.group(1)): text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)].strip()
            for i, m in enumerate(matches)}


def check_sections(text, required, name, errors):
    found = sections(text)
    for section in required:
        body = found.get(normalize(section))
        if body is None:
            errors.append(f"{name}: falta seccion {section}")
        elif not body or not re.sub(r"<!--.*?-->", "", body, flags=re.S).strip():
            errors.append(f"{name}: seccion vacia {section}")
        elif PLACEHOLDER.search(body):
            errors.append(f"{name}: seccion pendiente {section}")
    return found


def validate(root, stage="all"):
    root = Path(root).resolve()
    errors, warnings = [], []
    try:
        cfg = configuration(root)
        docs = cfg["documents"]
        if stage in ("1", "all"):
            prd = read_doc(root, docs["requirements"], errors)
            if prd is not None:
                check_sections(prd, cfg["requirements_sections"], docs["requirements"], errors)
        if stage in ("2", "all"):
            arq = read_doc(root, docs["architecture"], errors)
            if arq is not None:
                found = check_sections(arq, cfg["architecture_sections"], docs["architecture"], errors)
                diagram_text = found.get(normalize("Diagramas"), "")
                references = re.findall(r"\(([^)]+\.mmd)\)", diagram_text)
                if not references:
                    errors.append(f"{docs['architecture']}: falta referencia Mermaid .mmd")
                for ref in references:
                    relative_to_arch = str(Path(docs["architecture"]).parent / ref)
                    if not resolve_within(root, relative_to_arch).is_file():
                        errors.append(f"diagrama no encontrado: {ref}")
            guard = read_doc(root, docs["guardrails"], errors)
            if guard is not None:
                found = sections(guard)
                for title in ("Prohibido", "Obligatorio"):
                    body = found.get(normalize(title), "")
                    if not re.search(r"^\s*[-*]\s+\S", body, re.M) or PLACEHOLDER.search(body):
                        errors.append(f"{docs['guardrails']}: completar {title} con items")
            prd = read_doc(root, docs["requirements"], errors)
            if prd is not None:
                pending = sections(prd).get(normalize("Decisiones pendientes"), "")
                refs = set(ADR_REF.findall(pending))
                for ref in sorted(refs):
                    adr_dir = resolve_within(root, docs["adr_directory"])
                    candidates = list(adr_dir.glob(f"ADR-{ref}-*.md")) if adr_dir.is_dir() else []
                    if len(candidates) != 1:
                        errors.append(f"ADR-{ref}: se espera exactamente un documento")
                        continue
                    content = candidates[0].read_text(encoding="utf-8")
                    body = check_sections(content, ["Estado", "Contexto", "Decision", "Alternativas descartadas", "Consecuencias"], str(candidates[0].relative_to(root)), errors)
                    state = normalize(body.get("estado", "")).strip()
                    if state not in ("aceptada", "aceptado"):
                        errors.append(f"ADR-{ref}: Estado debe ser Aceptada")
                    if "por que no:" not in normalize(body.get("alternativas descartadas", "")):
                        errors.append(f"ADR-{ref}: justificar alternativas con 'Por que no:'")
                if re.search(r"^\s*[-*]\s+(?!.*ADR-\d{4}).+", pending, re.M):
                    errors.append("Decisiones pendientes: hay items sin referencia ADR")
        validate_profiles(root, docs, cfg.get("profiles", []), stage, errors)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"configuracion/lectura invalida: {exc}")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Valida especificaciones SDD en un proyecto destino")
    parser.add_argument("--project", required=True, help="Ruta a proyecto, no al repositorio del agente")
    parser.add_argument("--stage", choices=("1", "2", "all"), default="all")
    args = parser.parse_args()
    errors, warnings = validate(args.project, args.stage)
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")
    if errors:
        return 1
    print(f"[OK] Etapa {args.stage}: especificacion completa")
    return 0


if __name__ == "__main__":
    sys.exit(main())

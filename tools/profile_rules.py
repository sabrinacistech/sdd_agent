"""Composable project profiles for SDD validation.

Built-in profile definitions live under profiles/<name>/policy.json.
Project configuration can set "profiles": ["java-spring-boot", "channel-cutting"].
"""
import json
import re
from pathlib import Path

PROFILE_ROOT = Path(__file__).resolve().parents[1] / "profiles"
ITEM = re.compile(r"^\s*[-*]\s+\S", re.M)
METRIC = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|ms|s|seg|segundos|min|h|horas|d[ií]as|rps|tps|usuarios|canales|operaciones|<=|>=|<|>)|(?:<=|>=|<|>)\s*\d", re.I)


def _normal(text):
    return " ".join(text.casefold().translate(str.maketrans("áéíóúüñ", "aeiouun")).split())


def _sections(text):
    header = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.M)
    matches = list(header.finditer(text))
    return {_normal(m.group(1)): text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)].strip()
            for i, m in enumerate(matches)}


def load_profiles(names):
    if not isinstance(names, list) or not all(isinstance(x, str) and re.fullmatch(r"[a-z][a-z0-9-]*", x) for x in names):
        raise ValueError("profiles debe ser una lista de nombres validos")
    loaded = []
    for name in names:
        path = PROFILE_ROOT / name / "policy.json"
        if not path.is_file():
            raise ValueError(f"perfil desconocido: {name}")
        obj = json.loads(path.read_text(encoding="utf-8"))
        if obj.get("name") != name or obj.get("schema_version") != 1:
            raise ValueError(f"perfil invalido: {name}")
        loaded.append(obj)
    return loaded


def validate_profiles(root, docs, names, stage, errors):
    for profile in load_profiles(names):
        for section_stage, key, doc_key in (("1", "requirements", "requirements"), ("2", "architecture", "architecture")):
            if stage not in (section_stage, "all"):
                continue
            path = root / docs[doc_key]
            # Path is already validated by project_policy.configuration.
            if not path.is_file():
                continue  # Base validator reports missing document.
            sections = _sections(path.read_text(encoding="utf-8"))
            rules = profile.get(key, {})
            for title in rules.get("sections", []):
                if not sections.get(_normal(title)):
                    errors.append(f"[{profile['name']}] {doc_key}: falta seccion {title}")
            for title in rules.get("list_sections", []):
                body = sections.get(_normal(title), "")
                if not ITEM.search(body):
                    errors.append(f"[{profile['name']}] {doc_key}: {title} requiere lista de items")
            for title in rules.get("metric_sections", []):
                body = sections.get(_normal(title), "")
                entries = [l.strip() for l in body.splitlines() if ITEM.match(l)]
                if not entries or any(not METRIC.search(l) for l in entries):
                    errors.append(f"[{profile['name']}] {doc_key}: {title} requiere metricas en cada item")

"""Regression tests for the reusable, project-scoped validator."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from project_policy import validate


class ProjectPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "sdd.json").write_text(json.dumps({
            "schema_version": 1,
            "profile": "generic",
            "requirements_sections": ["Objetivo", "Decisiones pendientes"],
            "architecture_sections": ["Componentes", "Diagramas"],
        }), encoding="utf-8")

    def write(self, rel, data):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")

    def complete(self):
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nResolver problema X.\n\n## Decisiones pendientes\nSin decisiones irreversibles.\n")
        self.write("docs/02-diseno/arquitectura.md",
                   "## Componentes\nServicio X\n\n## Diagramas\n[Diagrama](diagramas/base.mmd)\n")
        self.write("docs/02-diseno/diagramas/base.mmd", "graph TD; A-->B")
        self.write("docs/02-diseno/guardrails.md",
                   "## Prohibido\n- Acceso directo\n\n## Obligatorio\n- Trazabilidad\n")

    def test_missing_configuration_fails_closed(self):
        (self.root / "sdd.json").unlink()
        self.assertTrue(validate(self.root)[0])

    def test_complete_project(self):
        self.complete()
        self.assertEqual(validate(self.root)[0], [])

    def test_missing_requirements(self):
        self.assertTrue(validate(self.root, "1")[0])

    def test_placeholder_blocks(self):
        self.complete()
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nTBD\n\n## Decisiones pendientes\nSin decisiones.\n")
        self.assertTrue(validate(self.root, "1")[0])

    def test_adr_requires_acceptance(self):
        self.complete()
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nProblema X\n\n## Decisiones pendientes\n- ADR-0001: motor\n")
        self.write("docs/02-diseno/adr/ADR-0001-motor.md",
                   "## Estado\nPropuesta\n## Contexto\nX\n## Decision\nY\n"
                   "## Alternativas descartadas\nZ. Por qué no: costo.\n## Consecuencias\nW\n")
        self.assertTrue(any("Estado" in x for x in validate(self.root, "2")[0]))

    def test_common_spanish_words_are_not_placeholders(self):
        self.complete()
        for text in ("Migrar todo el catalogo.", "Completar el alta en 2 pasos.",
                     "Queda pendiente de firma del cliente."):
            with self.subTest(text=text):
                self.write("docs/01-requisitos/PRD.md",
                           f"## Objetivo\n{text}\n\n## Decisiones pendientes\nNinguna.\n")
                self.assertEqual(validate(self.root, "1")[0], [])
        for text in ("TODO", "TBD", "<Por definir>", "<completar>"):
            with self.subTest(text=text):
                self.write("docs/01-requisitos/PRD.md",
                           f"## Objetivo\n{text}\n\n## Decisiones pendientes\nNinguna.\n")
                self.assertTrue(validate(self.root, "1")[0])

    def test_invalid_diagram_path_keeps_other_errors(self):
        self.complete()
        self.write("docs/02-diseno/arquitectura.md",
                   "## Componentes\nServicio X\n\n## Diagramas\n[d](../../../x.mmd)\n")
        self.write("docs/02-diseno/guardrails.md", "## Prohibido\n\n## Obligatorio\n- Trazabilidad\n")
        errors = validate(self.root)[0]
        self.assertTrue(any("ruta invalida" in e for e in errors))
        self.assertTrue(any("Prohibido" in e for e in errors))

    def test_missing_prd_reported_once(self):
        self.complete()
        (self.root / "docs/01-requisitos/PRD.md").unlink()
        errors = validate(self.root)[0]
        self.assertEqual(sum("PRD.md: no existe" in e for e in errors), 1)
        self.assertEqual(sum("PRD.md: no existe" in e for e in validate(self.root, "2")[0]), 1)

    def adr(self, state):
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nProblema X\n\n## Decisiones pendientes\n- ADR-0001: motor\n")
        self.write("docs/02-diseno/adr/ADR-0001-motor.md",
                   f"## Estado\n{state}\n## Contexto\nX\n## Decision\nY\n"
                   "## Alternativas descartadas\nZ. Por qué no: costo.\n## Consecuencias\nW\n")
        return [e for e in validate(self.root, "2")[0] if "Estado" in e]

    def test_adr_state_accepts_date_but_not_negation(self):
        self.complete()
        self.assertEqual(self.adr("Aceptada el 2026-01-10"), [])
        self.assertEqual(self.adr("Aceptado."), [])
        self.assertTrue(self.adr("No aceptada"))
        self.assertTrue(self.adr("Propuesta (pendiente de aceptada)"))

    def test_decisions_section_is_configurable(self):
        self.complete()
        cfg = json.loads((self.root / "sdd.json").read_text())
        cfg["requirements_sections"] = ["Objetivo", "Decisiones que requieren ADR"]
        cfg["decisions_section"] = "Decisiones que requieren ADR"
        (self.root / "sdd.json").write_text(json.dumps(cfg))
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nX\n\n## Decisiones que requieren ADR\n- Elegir motor sin ADR\n")
        self.assertTrue(any("sin referencia ADR" in e for e in validate(self.root)[0]))

    def test_headings_inside_code_fences_are_ignored(self):
        self.complete()
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nX\n```md\n## Decisiones pendientes\nNinguna.\n```\n")
        self.assertTrue(any("falta seccion Decisiones pendientes" in e for e in validate(self.root, "1")[0]))

    def test_path_traversal_rejected(self):
        cfg = json.loads((self.root / "sdd.json").read_text())
        cfg["documents"] = {"requirements": "../outside.md"}
        (self.root / "sdd.json").write_text(json.dumps(cfg))
        self.assertTrue(validate(self.root)[0])


if __name__ == "__main__":
    unittest.main()

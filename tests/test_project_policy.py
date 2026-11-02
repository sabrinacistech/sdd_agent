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

    def test_path_traversal_rejected(self):
        cfg = json.loads((self.root / "sdd.json").read_text())
        cfg["documents"] = {"requirements": "../outside.md"}
        (self.root / "sdd.json").write_text(json.dumps(cfg))
        self.assertTrue(validate(self.root)[0])


if __name__ == "__main__":
    unittest.main()

"""Profile composition and validation tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from project_policy import validate


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {
            "schema_version": 1,
            "profiles": [],
            "requirements_sections": ["Objetivo", "Decisiones pendientes"],
            "architecture_sections": ["Componentes", "Diagramas"]
        }
        self.save_config()
        self.write("docs/01-requisitos/PRD.md",
                   "## Objetivo\nResolver X\n## Decisiones pendientes\nSin decisiones\n")

    def save_config(self):
        (self.root / "sdd.json").write_text(json.dumps(self.config), encoding="utf-8")

    def write(self, path, content):
        f = self.root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")

    def test_unrecognized_profile_fails_closed(self):
        self.config["profiles"] = ["not-a-profile"]
        self.save_config()
        self.assertTrue(any("desconocido" in e for e in validate(self.root, "1")[0]))

    def test_channel_requirements_missing(self):
        self.config["profiles"] = ["channel-cutting"]
        self.save_config()
        errors, _ = validate(self.root, "1")
        self.assertTrue(any("Canales afectados" in e for e in errors))

    def test_channel_requirements_satisfied(self):
        self.config["profiles"] = ["channel-cutting"]
        self.save_config()
        self.write("docs/01-requisitos/PRD.md", """## Objetivo
Resolver X
## Decisiones pendientes
Sin decisiones
## Canales afectados
- Aplicacion web
## Criterio de corte
Operacion manual con autorizacion
## Ventana y blast radius
Ventana sabado, 200 usuarios
## SLO/SLI impactados
Latencia p95
## Plan de rollback
- Revertir configuracion
## Criterios de aceptacion
- p95 < 300 ms
""")
        self.assertEqual(validate(self.root, "1")[0], [])

    def test_java_profile_requires_architecture_sections(self):
        self.config["profiles"] = ["java-spring-boot"]
        self.save_config()
        self.write("docs/02-diseno/arquitectura.md",
                   "## Componentes\nServicio X\n## Diagramas\n[Diagrama](diagramas/main.mmd)\n")
        self.write("docs/02-diseno/diagramas/main.mmd", "graph TD; A-->B")
        self.write("docs/02-diseno/guardrails.md",
                   "## Prohibido\n- Acceso directo\n## Obligatorio\n- Auditoria\n")
        errors, _ = validate(self.root, "2")
        self.assertTrue(any("Contratos API" in e for e in errors))

    def test_profiles_can_combine(self):
        self.config["profiles"] = ["channel-cutting", "java-spring-boot"]
        self.save_config()
        errors, _ = validate(self.root, "1")
        self.assertTrue(any("[channel-cutting]" in e for e in errors))


if __name__ == "__main__":
    unittest.main()

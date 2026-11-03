"""Spec Gate PR3 tests: direct decisions, integration and installer."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from spec_gate_hook import decide
from install_spec_gate import install, MARKER


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "sdd.json").write_text(json.dumps({
            "schema_version": 1,
            "profiles": [],
            "requirements_sections": ["Objetivo", "Decisiones pendientes"],
            "architecture_sections": ["Componentes", "Diagramas"]
        }), encoding="utf-8")

    def write(self, rel, value):
        file = self.root / rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(value, encoding="utf-8")

    def event(self, tool, **params):
        return {"tool_name": tool, "tool_input": params, "cwd": str(self.root)}

    def make_complete(self):
        self.write("docs/01-requisitos/PRD.md", "## Objetivo\nX\n## Decisiones pendientes\nSin decisiones.\n")
        self.write("docs/02-diseno/arquitectura.md",
                   "## Componentes\nServicio\n## Diagramas\n[Figura](diagramas/main.mmd)\n")
        self.write("docs/02-diseno/diagramas/main.mmd", "graph TD; A-->B")
        self.write("docs/02-diseno/guardrails.md",
                   "## Prohibido\n- Riesgo\n## Obligatorio\n- Auditar\n")

    def test_blocks_product_write_without_spec(self):
        allowed, reason = decide(self.root, self.event("Write", file_path=str(self.root / "src/a.py")))
        self.assertFalse(allowed)
        self.assertIn("SPEC GATE", reason)

    def test_allows_docs_and_sdd_json_to_fix_spec(self):
        for rel in ("docs/01-requisitos/PRD.md", "docs/02-diseno/arquitectura.md", "sdd.json"):
            with self.subTest(rel=rel):
                self.assertTrue(decide(self.root, self.event("Edit", file_path=str(self.root / rel)))[0])

    def test_does_not_exempt_hooks_tools_or_readme(self):
        for rel in (".claude/settings.local.json", "tools/evil.py", "README.md"):
            with self.subTest(rel=rel):
                self.assertFalse(decide(self.root, self.event("Write", file_path=str(self.root / rel)))[0])

    def test_outside_project_denied_even_when_complete(self):
        self.make_complete()
        self.assertFalse(decide(self.root, self.event("Write", file_path=str(self.root.parent / "other.py")))[0])

    def test_relative_path_uses_cwd(self):
        self.assertTrue(decide(self.root, self.event("Write", file_path="docs/01-requisitos/PRD.md"))[0])
        self.assertFalse(decide(self.root, self.event("Edit", file_path="../outside.py"))[0])
        self.assertFalse(decide(self.root, {"tool_name": "Write", "tool_input": {"file_path": "docs/a.md"}})[0])

    def test_shell_blocked_when_spec_missing(self):
        for name in ("Bash", "PowerShell"):
            self.assertFalse(decide(self.root, self.event(name, command="echo x > src/a.py"))[0])

    def test_shell_allowed_when_complete(self):
        self.make_complete()
        self.assertTrue(decide(self.root, self.event("Bash", command="python -m unittest"))[0])
        self.assertTrue(decide(self.root, self.event("NotebookEdit", notebook_path=str(self.root / "notebook.ipynb")))[0])

    def test_missing_or_unknown_payload_denied(self):
        self.assertFalse(decide(self.root, {})[0])
        self.assertFalse(decide(self.root, self.event("Write"))[0])
        self.assertFalse(decide(self.root, self.event("Unknown", command="x"))[0])

    def test_profile_errors_close_gate(self):
        cfg = json.loads((self.root / "sdd.json").read_text())
        cfg["profiles"] = ["channel-cutting"]
        (self.root / "sdd.json").write_text(json.dumps(cfg))
        self.make_complete()
        self.assertFalse(decide(self.root, self.event("Write", file_path=str(self.root / "src/a.java")))[0])

    def test_installer_preserves_other_hooks_and_is_idempotent(self):
        path = self.root / ".claude/settings.local.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"permissions": {"allow": ["Read"]},
                                    "hooks": {"PreToolUse": [{"matcher": "Other", "hooks": []}]}}))
        install(self.root)
        install(self.root)
        cfg = json.loads(path.read_text())
        self.assertEqual(cfg["permissions"]["allow"], ["Read"])
        self.assertEqual(len(cfg["hooks"]["PreToolUse"]), 2)
        self.assertEqual(cfg["hooks"]["PreToolUse"][1]["matcher"], MARKER)
        self.assertIn(str(self.root), cfg["hooks"]["PreToolUse"][1]["hooks"][0]["args"])
        self.assertEqual(cfg["hooks"]["PreToolUse"][1]["hooks"][0]["onFailure"], "block")

    def test_installer_requires_sdd_config(self):
        (self.root / "sdd.json").unlink()
        with self.assertRaises(ValueError):
            install(self.root)


if __name__ == "__main__":
    unittest.main()

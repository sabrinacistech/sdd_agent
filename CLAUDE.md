# channel-cutting — Cancelación de canales

Proyecto de Galicia — SRE. El trabajo sigue un SDLC asistido por IA con compuerta de
especificación: **no se escribe código de producto hasta que Requisitos y Diseño estén
completos y validados.**

## Flujo

| Etapa | Comando | Salida | Valida |
|---|---|---|---|
| 1 — Requisitos | `/requisitos` | `docs/01-requisitos/PRD.md` | `python tools/spec_lint.py --stage 1` |
| 2 — Diseño | `/diseno` | `docs/02-diseno/` (arquitectura, ADRs, guardarraíles, diagramas) | `python tools/spec_lint.py --stage 2` |

Skill de referencia: `/arquetipos-pom-paas` — qué parent (POM, PaaS o Commons) usar
según la capa del componente. Consultarlo en la Etapa 2 al decidir el stack de cada
servicio; la elección lleva ADR.

## Spec Gate

Un hook `PreToolUse` (`tools/spec_gate_hook.py`) corre el validador antes de cada
`Write`/`Edit`. Si la spec está incompleta, **bloquea la escritura de código de
producto** y devuelve la lista de lo que falta.

Quedan siempre editables: `docs/`, `tools/`, `.claude/`, `CLAUDE.md`, `README.md` —
para poder completar justamente lo que el gate reclama.

Verificación manual en cualquier momento:

```bash
python tools/spec_lint.py
```

## Reglas permanentes

- **Los criterios de aceptación llevan número y unidad.** Sin métrica no son
  verificables y la Etapa 5 (revisión) no tiene contra qué contrastar.
- **Toda decisión irreversible lleva ADR**, con alternativas descartadas y su porqué.
  Corregir una decisión de arquitectura tarde es el error más caro del ciclo.
- **Decirle al agente qué evitar es tan importante como decirle qué hacer.** Los
  guardarraíles viven en `docs/02-diseno/guardrails.md` y aplican a todo el trabajo.
- **No inventar requisitos.** Si falta un dato, dejar el placeholder y señalar que
  bloquea el avance.
- Dominio sensible: un corte de canales impacta clientes reales. El plan de rollback
  no es opcional.

## Referencia

Las etapas 3 a 7 (planificación, implementación, revisión, despliegue, operaciones)
siguen el mismo marco y todavía no están instrumentadas en este repo.

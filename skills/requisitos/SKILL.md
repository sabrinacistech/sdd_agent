---
name: requisitos
description: Etapa 1 del SDLC basado en especificaciones para proyectos de cualquier dominio. Elicita necesidades y produce el PRD del proyecto destino según sdd.json y sus perfiles.
---

# Etapa 1 — Requisitos del proyecto destino

No escribir código ni decidir arquitectura durante esta etapa. No inventar requisitos.

## Proyecto y configuración

1. Identificar el directorio raíz del **proyecto destino** (no asumir que es el directorio del agente).
2. Leer `<proyecto>/sdd.json`. Si falta, explicar cómo iniciar desde `examples/generic/sdd.json`; no inventar un perfil.
3. Leer los perfiles configurados bajo `profiles/<nombre>/policy.json`, junto con cualquier skill de referencia aplicable.
4. Leer el PRD del proyecto en la ruta declarada por `documents.requirements` (por defecto `docs/01-requisitos/PRD.md`). Conservar el contenido existente.

## Procedimiento

1. Ejecutar `python <sdd_agent>/tools/project_policy.py --project <proyecto> --stage 1`.
2. Preguntar por bloques pequeños, empezando por requisitos faltantes o inciertos.
3. Registrar la información confirmada y etiquetar los puntos pendientes; no completarlos por suposición.
4. Incluir objetivos, actores, alcance y exclusiones, requisitos funcionales/no funcionales, dependencias, criterios de aceptación y decisiones pendientes de ADR.
5. Aplicar las preguntas especializadas **solo** si el perfil correspondiente está seleccionado.
6. Volver a ejecutar el validador hasta que no haya errores.

## Condiciones de salida

- PRD completo según configuración y perfiles.
- Decisiones costosas de revertir identificadas para la Etapa 2.
- El resultado del linter es una revisión **estructural**, no una aprobación de negocio ni autorización automática para implementar.

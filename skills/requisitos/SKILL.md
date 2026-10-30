---
name: requisitos
description: Etapa 1 del SDLC asistido por IA. Entrevista estructurada para definir qué se construye, por qué, para quién y con qué alcance en un corte/cancelación de canales, y producir docs/01-requisitos/PRD.md completo y verificable. Usar al arrancar una iniciativa, antes de cualquier decisión de diseño o de código.
---

# Etapa 1 — Recolección de requisitos

Tu trabajo acá **no es escribir código ni proponer arquitectura**. Es conseguir que
el PRD quede completo y que cada afirmación sea verificable.

## Procedimiento

1. Leé `docs/01-requisitos/PRD.md`. Si ya tiene contenido, trabajá sobre él; no lo
   reescribas de cero.
2. Corré `python tools/spec_lint.py --stage 1` para ver exactamente qué falta.
3. Preguntá **de a un bloque por vez**, no las diez secciones juntas. Empezá por lo
   que el linter marca como faltante.
4. Después de cada bloque, escribí lo acordado en el PRD y volvé a correr el linter.
5. Terminá cuando `--stage 1` devuelva `[OK]`.

## Preguntas obligatorias del dominio

Un corte de canales tiene riesgo de impacto directo sobre clientes. No cierres la
etapa sin respuesta explícita a:

- **Canales afectados**: enumerados uno por uno (homebanking, app mobile, ATM, call
  center, cajas, APIs de terceros...). "Todos" no es una respuesta.
- **Criterio de corte**: qué condición exacta dispara la cancelación, y quién la
  evalúa. Si es manual, quién firma.
- **Ventana y blast radius**: cuándo se ejecuta y a cuántos clientes/operaciones
  alcanza en el peor caso.
- **SLO/SLI impactados**: qué indicadores se degradan y cuánto es tolerable.
- **Dependencias**: qué sistemas upstream alimentan la decisión y qué downstream
  consume el resultado.
- **Plan de rollback**: pasos concretos de reversión, cuánto tardan, y si el corte
  es reversible o no. Si no es reversible, decilo explícitamente en esta sección.

## Reglas de calidad

- **Cada criterio de aceptación lleva número y unidad.** "Rápido" no es un criterio;
  "p95 < 300 ms" sí. El linter rechaza los que no tengan métrica.
- **Si el usuario no sabe una respuesta, no la inventes.** Dejá el placeholder y
  decile que esa sección bloquea el avance. Un `TBD` visible es mejor que un
  requisito fabricado.
- **No propongas solución técnica.** Si aparece una decisión de arquitectura durante
  la conversación, anotala en la sección 10 (Decisiones que requieren ADR) y seguí.
  Se resuelve en `/diseno`.

## Salida

- `docs/01-requisitos/PRD.md` completo.
- La sección 10 con la lista de decisiones que la Etapa 2 tiene que cerrar vía ADR.

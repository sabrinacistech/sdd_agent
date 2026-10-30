---
name: diseno
description: Etapa 2 del SDLC asistido por IA (Spec-Driven Development). Convierte el PRD en arquitectura, ADRs, guardarraíles y diagramas versionados bajo docs/02-diseno/. Usar después de /requisitos y antes de planificar o implementar, o cuando haya que cerrar una decisión técnica irreversible.
---

# Etapa 2 — Diseño del sistema (Spec-Driven Development)

El objetivo es dejar escrito, con suficiente detalle, **cómo debe construirse el
sistema y qué no debe hacerse**, para que la implementación sea ejecución y no
interpretación.

## Precondición

Corré `python tools/spec_lint.py --stage 1`. Si la Etapa 1 no pasa, **parala acá**:
diseñar sobre requisitos incompletos es exactamente el error caro que esta compuerta
existe para evitar. Decile al usuario qué falta y ofrecé `/requisitos`.

## Procedimiento

1. Leé `docs/01-requisitos/PRD.md` entero, con atención a la sección 10.
2. Completá `docs/02-diseno/arquitectura.md`: vista general, componentes, stack,
   patrones, seguridad, restricciones técnicas y diagramas.
3. Por **cada** decisión de la sección 10 del PRD, creá un ADR en
   `docs/02-diseno/adr/ADR-NNNN-slug.md` a partir de `ADR-0000-plantilla.md`.
   Numerá correlativamente y actualizá la referencia en el PRD.
4. Completá `docs/02-diseno/guardrails.md`.
5. Dibujá el diagrama en `docs/02-diseno/diagramas/*.mmd` (Mermaid, versionable) y
   referencialo desde la sección 7 de `arquitectura.md`.
6. Corré `python tools/spec_lint.py` hasta que devuelva `[OK]`.

## Qué cuenta como decisión que necesita ADR

Una decisión necesita ADR si **revertirla después cuesta caro**: elección de
mecanismo de corte, modelo de datos del estado del canal, estrategia de
idempotencia, sincrónico vs. asincrónico, dónde vive la fuente de verdad, cómo se
propaga el corte a cada canal, política de reintentos.

No necesita ADR lo que se cambia con un commit: nombres, formato de logs, layout de
carpetas.

## Reglas de calidad

- **Un ADR sin alternativas descartadas no es un ADR.** Cada uno debe explicar al
  menos una opción rechazada con `Por qué no:`. El linter lo exige.
- **El estado del ADR debe ser `Aceptada`** para que la compuerta deje implementar.
  Mientras esté en `Propuesta`, el gate sigue cerrado: eso es intencional.
- **Los guardarraíles son la parte que más se saltea y la que más rinde.** Escribí
  qué está *prohibido* (mínimo 3 items) con el mismo cuidado que lo obligatorio. Si
  no sabés qué prohibir, mirá el plan de rollback del PRD: todo lo que lo rompa va
  a la lista.
- **Seguridad no es una sección de relleno.** En un corte de canales: quién puede
  disparar el corte, cómo se audita, qué datos de cliente se tocan.

## Salida

- `docs/02-diseno/arquitectura.md` completo.
- Un ADR aceptado por cada decisión del PRD.
- `docs/02-diseno/guardrails.md` con prohibiciones explícitas.
- Al menos un diagrama `.mmd` existente y referenciado.

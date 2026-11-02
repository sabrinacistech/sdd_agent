---
name: diseno
description: Etapa 2 SDD reutilizable. Convierte el PRD del proyecto destino en arquitectura, ADR, guardrails y diagramas, aplicando perfiles de proyecto.
---

# Etapa 2 — Diseño técnico del proyecto destino

## Precondiciones

1. Resolver la raíz del proyecto destino y leer su `sdd.json`.
2. Ejecutar `python <sdd_agent>/tools/project_policy.py --project <proyecto> --stage 1`.
3. Si la validación falla, detener el diseño y completar requisitos mediante `/requisitos`.
4. No suponer aprobaciones humanas por un resultado `[OK]`.

## Procedimiento

1. Leer íntegramente el PRD (ruta `documents.requirements`).
2. Proponer componentes, límites, contratos, persistencia, seguridad, operaciones y patrones apropiados al contexto.
3. Aplicar solo las reglas de los perfiles configurados en `sdd.json`; las referencias especializadas (por ejemplo `arquetipos-pom-paas`) son opcionales y deben justificarse en su contexto.
4. Escribir `documents.architecture` y `documents.guardrails` según la configuración.
5. Documentar ADR por decisión relevante con contexto, alternativas descartadas, consecuencias y estado real. **Nunca marcar `Aceptada` sin aprobación de la persona responsable**.
6. Crear diagramas Mermaid versionados y enlazarlos con rutas relativas al documento de arquitectura.
7. Ejecutar `python <sdd_agent>/tools/project_policy.py --project <proyecto> --stage 2` y corregir errores.

## Condiciones de salida

- Arquitectura, guardrails y diagramas completos.
- ADR referenciados desde `Decisiones pendientes` del PRD y aprobados por quien corresponda.
- El validador comprueba estructura, no corrección técnica integral.

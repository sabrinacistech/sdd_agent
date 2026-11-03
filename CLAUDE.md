# SDD Agent — desarrollo guiado por especificaciones multiproyecto

Este repositorio contiene **instrucciones, skills y validadores** reutilizables, no el código del proyecto de producto. El proyecto destino mantiene sus documentos y un `sdd.json` en su propia raíz.

## Identificar proyecto

Antes de cualquier operación:
1. Solicitar o identificar explícitamente la raíz del proyecto destino. **No asumir** que es `sdd_agent`.
2. Leer `sdd.json` del proyecto. Si no existe, usar `examples/generic/sdd.json` como plantilla previa confirmación del usuario.
3. Leer `profiles/<nombre>/policy.json` correspondientes a la lista `profiles` de esa configuración. Ningún perfil de dominio se aplica de forma implícita.
4. Mantener los documentos en el repositorio del proyecto; no crear PRD o arquitectura del producto en `sdd_agent`.

## Flujo

| Etapa | Skill | Validación |
|---|---|---|
| 1 Requisitos | /requisitos | `python tools/project_policy.py --project <ruta-proyecto> --stage 1` |
| 2 Diseño | /diseno | `python tools/project_policy.py --project <ruta-proyecto> --stage 2` |

El motor genérico verifica estructura documental, no coherencia semántica ni aprobación humana. Las decisiones que requieran ADR necesitan aprobación de sus responsables. No iniciar implementación por el mero resultado de un linter.

## Perfiles

- `generic`: reglas comunes de base.
- `java-spring-boot`: secciones técnicas orientadas a servicios Java y Spring.
- `channel-cutting`: controles documentales de cancelación de canales.
- `arquetipos-pom-paas`: skill de referencia específica, invocar solo cuando corresponda a la plataforma.

Los perfiles son componibles mediante `sdd.json`. Ver `examples/` y `profiles/`.

## Compatibilidad y limitaciones

`tools/spec_lint.py` se conserva como validador legacy del dominio channel-cutting. `tools/spec_gate_hook.py` ahora usa `project_policy.py` para validar el **proyecto destino**, pero **solo se activa tras instalarlo en ese proyecto** con `python tools/install_spec_gate.py --project <ruta-proyecto>` y reiniciar Claude Code. Ver `docs/USO_SPEC_GATE.md`. El hook es un control de flujo para herramientas cubiertas, no una barrera de seguridad universal ni una aprobación humana.

## Principios

- No inventar requisitos ni decisiones.
- Separar requisitos funcionales de decisiones de arquitectura.
- Explicitar restricciones, observabilidad, seguridad y riesgo operativo según el proyecto.
- Mantener trazabilidad entre decisiones, documentos y criterios verificables.
- Etapas 3–7 aún no instrumentadas: planificación, implementación, revisión, despliegue y operaciones.

# Evolución de SDD Agent a multiproyecto

## Entrega 1 (implementada, PR #1)
- Motor de validación genérico en `tools/project_policy.py`, independiente de un dominio.
- Contrato `sdd.json` por proyecto destino (ejemplo en `examples/generic/sdd.json`).
- Pruebas de regresión y ADR que explica el desacoplamiento.
- Se conserva `tools/spec_lint.py` para no romper el proceso channel-cutting.

## Entrega 2 (mayormente implementada, PR #2–#4)
- [x] Skills `/requisitos` y `/diseno` adaptadas al proyecto destino y sus perfiles.
- [x] Perfiles componibles `generic`, `java-spring-boot` y `channel-cutting`.
- [x] Hook `tools/spec_gate_hook.py` integrado con el nuevo validador, con validación de rutas, e instalador por proyecto (`tools/install_spec_gate.py`).
- [x] Tests del hook y del instalador.
- [ ] Migrar sin pérdida las reglas restantes de `spec_lint.py` al perfil `channel-cutting` (por ejemplo, el mínimo de 3 items en `Prohibido` y el aviso de ADR huérfanos).
- [ ] Validar el comportamiento del hook en una sesión real de Claude Code (prueba manual descrita en `docs/USO_SPEC_GATE.md`).

## Entrega 3 (pendiente)
- Registro explícito del estado por etapa, aprobaciones verificables y trazabilidad.
- Añadir etapas 3–7 progresivamente.

## Restricción
No considerar un `[OK]` del linter como aprobación humana ni garantía de corrección técnica.

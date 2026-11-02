# Evolución de SDD Agent a multiproyecto

## Entrega 1 (implementada en esta rama)
- Motor de validación genérico en `tools/project_policy.py`, independiente de un dominio.
- Contrato `sdd.json` por proyecto destino (ejemplo en `examples/generic/sdd.json`).
- Pruebas de regresión y ADR que explica el desacoplamiento.
- Se conserva `tools/spec_lint.py` y el hook original para no romper el proceso channel-cutting.

## Entrega 2 (pendiente)
- Adaptar las skills `/requisitos` y `/diseno` para resolver el proyecto de trabajo y sus perfiles.
- Definir perfil legacy `channel-cutting` y migrar sus reglas sin pérdida.
- Integrar el nuevo validador con un hook que cubra los mecanismos de edición pertinentes, con validación de rutas, y registrar su configuración real.
- Ejecutar tests del hook y validar el comportamiento en una sesión Claude.

## Entrega 3 (pendiente)
- Registro explícito del estado por etapa, aprobaciones verificables y trazabilidad.
- Añadir etapas 3–7 progresivamente.

## Restricción
No considerar un `[OK]` del linter como aprobación humana ni garantía de corrección técnica.

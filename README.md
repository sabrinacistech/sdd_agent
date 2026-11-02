# SDD Agent — evolución multiproyecto

Repositorio de instrucciones, skills y herramientas para desarrollo guiado por especificaciones (SDD).

## Estado

La rama `feature/sdd-multiproyecto` incorpora **un primer incremento experimental**, sin reemplazar el flujo existente de cancelación de canales. El agente todavía no está integrado completamente con el nuevo motor.

## Validación multiproyecto (nueva)

1. Copiar `examples/generic/sdd.json` como `sdd.json` en la raíz del **proyecto destino**.
2. Crear los documentos del proyecto conforme a las rutas y secciones declaradas.
3. Desde el repositorio del agente, ejecutar:

```bash
python tools/project_policy.py --project /ruta/al/proyecto --stage 1
python tools/project_policy.py --project /ruta/al/proyecto --stage 2
python tools/project_policy.py --project /ruta/al/proyecto
```

La herramienta usa únicamente la biblioteca estándar de Python; requiere Python 3.9 o superior. Bloquea si la configuración no existe, si una ruta escapa del proyecto, si faltan secciones o diagramas, o si un ADR referenciado no tiene estado Aceptada.

## Validación legacy (conservada)

```bash
python tools/spec_lint.py --stage 1
python tools/spec_lint.py --stage 2
```

El hook `tools/spec_gate_hook.py` **todavía usa el validador original**. No debe interpretarse la nueva herramienta como una protección activa sobre las escrituras de Claude.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Diseño y siguientes pasos

Ver `docs/architecture/ADR-0001-separacion-agente-proyecto.md` y `docs/architecture/ROADMAP.md`.

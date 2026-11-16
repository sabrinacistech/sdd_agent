# SDD Agent — evolución multiproyecto

Repositorio de instrucciones, skills y herramientas para desarrollo guiado por especificaciones (SDD).

## Estado

El motor multiproyecto (`tools/project_policy.py`), los perfiles componibles y el Spec Gate por proyecto (`tools/spec_gate_hook.py`) están integrados. El flujo legacy de cancelación de canales (`tools/spec_lint.py`) se conserva. Las etapas 3–7 aún no están instrumentadas.

## Validación multiproyecto (nueva)

1. Copiar `examples/generic/sdd.json` como `sdd.json` en la raíz del **proyecto destino**.
2. Crear los documentos del proyecto conforme a las rutas y secciones declaradas.
3. Desde el repositorio del agente, ejecutar:

```bash
python tools/project_policy.py --project /ruta/al/proyecto --stage 1
python tools/project_policy.py --project /ruta/al/proyecto --stage 2
python tools/project_policy.py --project /ruta/al/proyecto
```

La herramienta usa únicamente la biblioteca estándar de Python; requiere Python 3.10 o superior. Bloquea si la configuración no existe, si una ruta escapa del proyecto, si faltan secciones o diagramas, si una sección contiene marcadores pendientes o si un ADR referenciado no tiene estado Aceptada.

Detalles de las reglas:

- **Marcadores pendientes:** `TBD`, `TODO`, `FIXME`, `PENDIENTE`, `COMPLETAR` y `XXX` solo cuentan en mayúsculas, porque «todo», «completar» o «pendiente» son palabras comunes en castellano. Los marcadores de plantilla `<por definir>`, `<completar>` y `<pendiente>` cuentan sin importar mayúsculas.
- **Estado del ADR:** debe empezar por «Aceptada» o «Aceptado»; se admite texto posterior, por ejemplo «Aceptada el 2026-01-10».
- **Sección de decisiones:** el título de la sección del PRD que lista decisiones con ADR se configura con `decisions_section` en `sdd.json` (por defecto, `Decisiones pendientes`).
- **Bloques de código:** los títulos `##` dentro de bloques de código no cuentan como secciones.

## Validación legacy (conservada)

```bash
python tools/spec_lint.py --root /ruta/al/proyecto --stage 1
python tools/spec_lint.py --root /ruta/al/proyecto --stage 2
```

`--root` es obligatorio: el validador legacy nunca asume que el proyecto es el repositorio del agente.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Diseño y siguientes pasos

Ver `docs/architecture/ADR-0001-separacion-agente-proyecto.md` y `docs/architecture/ROADMAP.md`.

## Perfiles por proyecto (PR #2)

El proyecto destino selecciona perfiles componibles mediante `sdd.json`:

```json
{
  "schema_version": 1,
  "profiles": ["java-spring-boot", "channel-cutting"]
}
```

Perfiles disponibles: `generic`, `java-spring-boot` y `channel-cutting`. Un proyecto sin `profiles` continúa usando las validaciones base del primer incremento. Se admite el campo `profile` por compatibilidad histórica.

Ejemplos: `examples/java-spring-boot/sdd.json`, `examples/channel-cutting/sdd.json`. Las políticas declarativas se encuentran en `profiles/*/policy.json`. Las nuevas skills de requisitos y diseño trabajan sobre el proyecto **destino** y sus documentos, no sobre el repositorio del agente.

**Limitaciones:** se validan secciones y algunos criterios documentales, pero no la calidad semántica de los diseños. Las secciones exigidas por un perfil también se rechazan si contienen marcadores pendientes. `tools/spec_gate_hook.py` aplica el mismo validador, con perfiles incluidos, pero solo protege el proyecto destino tras instalarlo con `tools/install_spec_gate.py` (ver más abajo).

Pruebas de regresión:

```bash
python -m unittest discover -s tests -v
```

## PR #3 — Activar Spec Gate en cada proyecto

```powershell
python tools/install_spec_gate.py --project "C:\\repoSRE\\mi-proyecto"
python -m unittest discover -s tests -v
```

El instalador modifica `.claude/settings.local.json` del **proyecto destino**, preserva hooks previos y usa `onFailure: block`. Debe ejecutarse en cada computadora donde se quiera activar el control y reiniciar Claude Code.

Mientras el gate está cerrado, Claude solo puede editar los documentos de especificación: lo que está bajo `docs/`, los documentos y el directorio de ADR declarados en `sdd.json`, y los diagramas `.mmd`. **`sdd.json` queda bloqueado** para Claude hasta que el gate se abra, porque define la propia política; cambiarlo es una decisión de la persona responsable, fuera de Claude Code. Aun así, conviene revisar los cambios a `sdd.json` en code review o CI. Más información en `docs/USO_SPEC_GATE.md`.

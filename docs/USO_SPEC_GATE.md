# PR #3 — Instalación del Spec Gate multiproyecto

## Requisitos previos
- Python 3.10+ accesible desde la máquina que ejecuta Claude Code.
- Proyecto destino con `sdd.json` (ver `examples/`).
- Claude Code v2.1.295 o superior, necesario para `onFailure: block`.
- Una sesión de Claude Code que confíe en el directorio del proyecto.

## Instalación en Windows (PowerShell)

Dentro del repositorio del agente:

```powershell
python tools/install_spec_gate.py --project "C:\\repoSRE\\mi-proyecto"
```

El script escribe o actualiza `C:\\repoSRE\\mi-proyecto\\.claude\\settings.local.json` sin reemplazar otros hooks. Vincula rutas absolutas del ejecutable Python, del script de SDD y del proyecto; ejecutarlo de nuevo después de mover las carpetas. **No compartir este archivo ni versionarlo**.

Cierre y reinicio de Claude Code obligatorios para volver a cargar los hooks. Comprobar su presencia mediante `/hooks`.

## Matriz de decisiones

| Intento | Especificación incompleta | Especificación completa |
|---|---|---|
| Write/Edit en `docs/` del proyecto | Permitido | Permitido |
| Write/Edit en `sdd.json` | Permitido | Permitido |
| Write/Edit en `src/`, `tools/`, `.claude/` u otras rutas | Bloqueado | Permitido |
| NotebookEdit | Mismas reglas de ruta | Permitido |
| Bash/PowerShell (cualquier comando) | Bloqueado | Permitido |
| Escritura fuera del proyecto | Bloqueada | Bloqueada |

Los comandos Shell se bloquean sin analizar su contenido; para completar una especificación, editar los documentos con herramientas Write/Edit. Para ejecutar manualmente el validador en PowerShell **fuera de Claude Code**, usar:

```powershell
python tools/project_policy.py --project "C:\\repoSRE\\mi-proyecto"
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Para comprobar el bloqueo desde Claude Code: iniciar una sesión en el directorio de un proyecto con especificaciones incompletas e intentar escribir `src/probe.txt` con Write. Debe bloquear. Intentar después escribir `docs/01-requisitos/PRD.md` para completar requisitos. Debe permitir.

## Límites

El hook solo cubre las herramientas que coincidan con su matcher. No sustituye permisos de archivos, controles de CI ni revisión humana. Un resultado `[OK]` del linter no implica que el diseño esté aprobado. Si se necesita restringir también herramientas MCP específicas, habrá que definir hooks adicionales por nombre y esquema. Revisar en Claude Code la configuración y los permisos efectivos antes de confiar en el mecanismo como control de proceso.

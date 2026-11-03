# ADR-0003 — Spec Gate por proyecto destino

## Estado
Propuesta; pendiente de aprobación explícita.

## Contexto
El antiguo `spec_gate_hook.py` dependía de rutas dentro de `sdd_agent`, eximía archivos de código internos y no estaba configurado en un proyecto de Claude Code. Los perfiles del PR #2 ya permiten validar un proyecto destino mediante `sdd.json`.

## Decisión
Implementar un hook `PreToolUse` instalado **por proyecto destino** y vinculado explícitamente a su ruta absoluta mediante `--project`. El hook utiliza `project_policy.validate(..., "all")`. Mientras la especificación esté incompleta, solo permite `Write/Edit/MultiEdit/NotebookEdit` para documentos bajo `docs/` y `sdd.json`; bloquea comandos `Bash/PowerShell` por ser imposibles de clasificar con fiabilidad. Los archivos fuera del proyecto no pueden editarse mediante las herramientas cubiertas.

La instalación se realiza en `.claude/settings.local.json` del proyecto destino, preservando configuraciones existentes; invoca Python en modo exec con argumentos separados y `onFailure: block`.

## Alternativas descartadas
- Analizar comandos shell mediante expresiones regulares. Por qué no: pipes, redirecciones, ejecución indirecta y múltiples subcomandos permiten falsos negativos.
- Usar una raíz de proyecto implícita en el script del agente. Por qué no: provoca validaciones del repositorio incorrecto.
- Escribir rutas absolutas en `.claude/settings.json` versionado. Por qué no: no son portables entre computadoras.

## Consecuencias
El bloqueo es intencionalmente conservador: incluso comandos shell de solo lectura quedan bloqueados mientras las especificaciones estén incompletas; los documentos podrán editarse con las herramientas cubiertas. El hook se instala y se activa localmente, no basta con clonar el agente. Requiere Claude Code compatible con `onFailure: block` (v2.1.295+).

**Límite de seguridad:** no constituye sandbox ni control de acceso: no cubre escrituras vía herramientas MCP no configuradas, operaciones externas a Claude, cambios deliberados a la configuración ni acciones cuando el hook está deshabilitado. El validador revisa principalmente estructura, no aprobación humana ni calidad semántica.

# ADR-0001: Separar agente SDD de proyectos gestionados

## Estado
Propuesta (pendiente de revisión)

## Contexto
El repositorio actual mezcla instrucciones SDD generales con requisitos específicos de cancelación de canales. El linter original presupone documentos en el propio repositorio del agente.

## Decision
Mantener el motor y las skills generales en sdd_agent; cada proyecto destino conserva su configuración sdd.json y documentos bajo docs/. Introducir un validador genérico independiente, basado en Python estándar, sin modificar todavía el validador especializado existente.

## Alternativas descartadas
- Copiar todo el agente en cada proyecto. Por qué no: deriva y duplicación de reglas.
- Reemplazar inmediatamente el linter original. Por qué no: elimina controles específicos del dominio sin una ruta de migración comprobada.

## Consecuencias
La ejecución requiere indicar explícitamente --project; el perfil genérico pasa a estar disponible. En esta primera entrega el perfil channel-cutting continúa soportado por la herramienta legacy, no por el nuevo validador.

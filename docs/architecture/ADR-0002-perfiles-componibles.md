# ADR-0002 — Perfiles SDD componibles

## Estado
Propuesta (pendiente de aprobación explícita)

## Contexto
El primer incremento permite validar proyectos independientes, pero solo el perfil genérico. Requisitos y diseño requieren reglas por dominio y stack sin duplicar el core.

## Decisión
Introducir `profiles/<name>/policy.json` con reglas declarativas por etapa. Cada proyecto enumera `profiles` en su `sdd.json`, permitiendo combinaciones. El validador sigue siendo independiente del proyecto destino y rechaza perfiles desconocidos.

## Alternativas descartadas
- Una copia del validador por dominio. Por qué no: provoca deriva y duplicación.
- Cargar Python ejecutable desde cada proyecto. Por qué no: abre una superficie innecesaria de ejecución arbitraria.

## Consecuencias
Los perfiles están integrados en el repositorio del agente y sus reglas son estructurales. `java-spring-boot` exige secciones de diseño, pero no audita código Java. `channel-cutting` preserva preguntas importantes del dominio como perfil configurable. El antiguo `spec_lint.py` y el hook se conservan sin alteraciones; no existe todavía protección multiproyecto automática.

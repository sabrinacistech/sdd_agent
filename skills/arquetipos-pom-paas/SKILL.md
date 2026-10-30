---
name: arquetipos-pom-paas
description: Referencia de los arquetipos (parents) de la plataforma — POM, PaaS y Commons — y guía para elegir cuál usar en cada componente según su capa de arquitectura (BFF, POM, servicios de negocio, servicios de producto/Core, CIS). Usar al diseñar o revisar un componente backend, al escribir un ADR sobre el stack de un microservicio, o cuando haya dudas sobre si un servicio debe validar JWT, disponibilidad horaria o módulos por canal.
---

# Arquetipos POM, PaaS y Commons

Fuente: artículo interno de arquitectura *"Arquetipos POM y PaaS: qué son y diferencias
entre ellos"*. Este skill resume ese artículo y lo vuelve una guía de decisión. **No
agregues capacidades que el artículo no menciona**: si algo no está acá, es un dato a
confirmar con Arquitectura, no una suposición.

## Contexto: capas de la arquitectura

Cada componente de la plataforma atiende una capa, y cada capa tiene preocupaciones
distintas (un componente que agrega servicios para el frontend de un canal no se
preocupa por lo mismo que uno que integra un core legacy por un gateway):

1. BFF
2. Plataforma Omnicanal (POM)
3. Servicios de negocio
4. Servicios de producto (Core)
5. Componentes de integración (CIS)

Arquitectura publica *parents* con módulos que resuelven las preocupaciones comunes de
cada capa siguiendo pautas de diseño y buenas prácticas.

## Los tres parents

### PaaS

Módulos comunes para construir componentes de cualquier tipo en la plataforma.
**Recomendado** para servicios de negocio y servicios de producto, en llamadas internas
entre servicios backend donde **no hace falta validar permisos de usuario** entre ambos.

Incluye: trazabilidad · log · manejo de errores · Swagger.

### POM

Herramientas comunes para los servicios que soportan a los canales. **Obligatorio**
para componentes que proveen funcionalidad de canal y que en su diseño deben
contemplar omnicanalidad.

Incluye: trazabilidad · log · manejo de errores (**maestro de errores**) ·
**disponibilidad horaria con control de feriados y fuera de servicio** · **control de
módulos por canal** · **identificación y validación del cliente mediante JWT** · CORS ·
**integración con APIM** · Swagger.

### Commons

Para componentes y librerías internas que **no necesitan ser una API REST**. Trae la
misma versión de framework y dependencias externas que el parent POM y permite usar
los componentes de manejo de errores. **No incluye ni valida lógica de negocio**
(funcionalidades, disponibilidad, JWT, entre otros).

## Comparativa

| Capacidad | PaaS | POM | Commons |
|---|:-:|:-:|:-:|
| Trazabilidad | ✔ | ✔ | — |
| Log | ✔ | ✔ | — |
| Manejo de errores | ✔ | ✔ (maestro de errores) | ✔ (componentes) |
| Swagger | ✔ | ✔ | — |
| Disponibilidad horaria / feriados / fuera de servicio | — | ✔ | ✘ |
| Control de módulos por canal | — | ✔ | ✘ (funcionalidades) |
| Validación del cliente por JWT | — | ✔ | ✘ |
| CORS | — | ✔ | — |
| Integración con APIM | — | ✔ | — |
| Es API REST | ✔ | ✔ | ✘ |
| Uso | Recomendado (negocio / producto) | **Obligatorio** (funcionalidad de canal) | Librerías y componentes no REST |

`✘` = el artículo lo excluye explícitamente. `—` = el artículo no lo menciona para ese
parent; no asumir que está ni que falta, confirmar.

## Cómo elegir

Respondé en orden; la primera respuesta afirmativa decide:

1. **¿El componente provee funcionalidad de canal o debe contemplar omnicanalidad?**
   → **POM** (obligatorio, no es una preferencia).
2. **¿No necesita exponer una API REST (es una librería o componente interno)?**
   → **Commons**.
3. **¿Es un servicio de negocio o de producto, llamado por otro backend sin validar
   permisos de usuario entre ambos?** → **PaaS**.
4. Si nada encaja (p. ej. un BFF o un componente CIS, que el artículo lista como capas
   pero sin asignarles parent) → **no decidir**: dejá un placeholder y señalá que
   bloquea, según las reglas del proyecto.

Señales de alerta:

- Un servicio PaaS que necesita validar el JWT del cliente, la disponibilidad horaria o
  los módulos por canal **está en el parent equivocado**: esas capacidades son del POM.
- Un componente Commons que empieza a validar funcionalidades, disponibilidad o JWT
  viola el propósito del parent.

## Uso en este proyecto (channel-cutting)

- La elección de parent de un microservicio es costosa de revertir: **va en un ADR**
  (`docs/02-diseno/adr/`), con las alternativas descartadas y su porqué (p. ej. "PaaS —
  Por qué no: el servicio expone funcionalidad de canal, el POM es obligatorio").
- Citá este skill como fuente del criterio y registrá en el ADR qué capacidades del
  parent se usan (JWT, maestro de errores, disponibilidad, módulos por canal, APIM).
- Si la decisión depende de un dato no relevado (qué capa es el componente, si valida
  permisos de usuario, quién lo consume), **no lo inventes**: dejalo como hallazgo
  abierto en `docs/00-origen/` y en el PRD.
- Recordá la relación con lo ya relevado: el POM ya resuelve fuera de servicio por
  módulo y caché para OFB y App Mayorista (ver PRD y `meet-ofb-2026-10-20.md`). No
  dupliques en la botonera lo que el parent POM del destino ya provee sin un ADR que lo
  justifique.

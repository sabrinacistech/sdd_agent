"""Spec Gate - validador de completitud de las Etapas 1 (Requisitos) y 2 (Diseno).

Uso:
    python tools/spec_lint.py              # valida las dos etapas
    python tools/spec_lint.py --stage 1    # solo requisitos
    python tools/spec_lint.py --stage 2    # solo diseno
    python tools/spec_lint.py --quiet      # solo errores, sin resumen

Codigos de salida:
    0 = spec completa
    1 = hay errores bloqueantes
    2 = error de uso
"""

import argparse
import glob
import os
import re
import sys

PRD = "docs/01-requisitos/PRD.md"
ARQ = "docs/02-diseno/arquitectura.md"
GUARD = "docs/02-diseno/guardrails.md"
ADR_DIR = "docs/02-diseno/adr"

PRD_SECCIONES = [
    "1. Problema y objetivo",
    "2. Canales afectados",
    "3. Criterio de corte",
    "4. Alcance",
    "5. Ventana y blast radius",
    "6. SLO/SLI impactados",
    "7. Dependencias",
    "8. Plan de rollback",
    "9. Criterios de aceptacion",
    "10. Decisiones que requieren ADR",
]

ARQ_SECCIONES = [
    "1. Vista general",
    "2. Componentes",
    "3. Stack y librerias",
    "4. Patrones de arquitectura",
    "5. Seguridad",
    "6. Restricciones tecnicas",
    "7. Diagramas",
]

ADR_SECCIONES = ["Estado", "Contexto", "Decision", "Alternativas descartadas", "Consecuencias"]

# Marcadores que delatan una seccion sin completar.
#
# El angular admite saltos de linea (los placeholders de las plantillas se envuelven),
# pero NO puede empezar con espacio, digito o '=': eso descarta los comparadores de un
# criterio legitimo como "latencia < 300 ms y disponibilidad > 99%", que de otro modo
# se leeria como un placeholder "< 300 ms y disponibilidad >".
PLACEHOLDER_ANGULAR = re.compile(r"<(?![\s\d=])[^<>]{3,}>", re.DOTALL)

# Los literales van en mayuscula estricta: en castellano "todo" es una palabra comun.
PLACEHOLDER_LITERAL = re.compile(r"\b(TBD|TODO|FIXME|PENDIENTE|COMPLETAR|XXX)\b")

# Etiquetas HTML de 3+ caracteres que podrian confundirse con un placeholder.
TAGS_HTML = {"br/", "hr/", "code", "/code", "strong", "/strong", "sub", "/sub",
             "sup", "/sup", "kbd", "/kbd", "small", "/small", "span", "/span"}


def buscar_placeholder(texto):
    """Devuelve un fragmento del primer placeholder encontrado, o None."""
    for hit in PLACEHOLDER_ANGULAR.finditer(texto):
        contenido = hit.group(0)[1:-1]
        if contenido.lower() in TAGS_HTML or "://" in contenido:
            continue  # etiqueta HTML o URL entre angulares, no un hueco.
        frag = " ".join(hit.group(0).split())
        return frag if len(frag) <= 90 else frag[:87] + "..."
    hit = PLACEHOLDER_LITERAL.search(texto)
    return hit.group(0) if hit else None

# Un criterio es verificable si tiene un numero y una unidad o un comparador.
TIENE_NUMERO = re.compile(r"\d")
TIENE_UNIDAD = re.compile(
    r"%|<=|>=|<|>|=|\bms\b|\bseg\b|\bs\b|\bmin\b|\bhs?\b|\bd[ií]as?\b|"
    r"\brps\b|\btps\b|\bMB\b|\bGB\b|\bp\d{2}\b|\bcanal(es)?\b|\busuarios?\b",
    re.IGNORECASE,
)

ITEM = re.compile(r"^\s*[-*]\s+(.*)$")
ADR_REF = re.compile(r"ADR-(\d{4})")


_ACENTOS = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")


def _normalizar(texto):
    """Compara titulos ignorando acentos, mayusculas y espacios de mas."""
    return " ".join(texto.lower().translate(_ACENTOS).split())


def leer(root, rel):
    ruta = os.path.join(root, rel)
    if not os.path.isfile(ruta):
        return None
    with open(ruta, encoding="utf-8") as fh:
        return fh.read()


def secciones(texto, nivel="## "):
    """Devuelve {titulo_normalizado: [lineas del cuerpo]} para un nivel de heading."""
    out = {}
    actual = None
    for linea in texto.splitlines():
        if linea.startswith(nivel) and not linea.startswith(nivel + "#"):
            actual = _normalizar(linea[len(nivel):])
            out[actual] = []
        elif actual is not None:
            out[actual].append(linea)
    return out


def cuerpo_vacio(lineas):
    return not any(l.strip() and not l.strip().startswith("<!--") for l in lineas)


def items(lineas):
    return [m.group(1).strip() for l in lineas for m in [ITEM.match(l)] if m]


def _chequear_doc(texto, rel, requeridas, errores, nivel="## "):
    """Valida que existan todas las secciones, con cuerpo y sin placeholders."""
    presentes = secciones(texto, nivel)
    for titulo in requeridas:
        clave = _normalizar(titulo)
        if clave not in presentes:
            errores.append(f"{rel}: falta la seccion '{nivel}{titulo}'")
            continue
        cuerpo = presentes[clave]
        if cuerpo_vacio(cuerpo):
            errores.append(f"{rel}: la seccion '{titulo}' esta vacia")
            continue
        frag = buscar_placeholder("\n".join(cuerpo))
        if frag:
            errores.append(f"{rel}: '{titulo}' sin completar -> {frag}")
    return presentes


def check_requisitos(root, errores, warnings):
    texto = leer(root, PRD)
    if texto is None:
        errores.append(f"{PRD}: no existe. Ejecuta /requisitos para generarlo.")
        return

    presentes = _chequear_doc(texto, PRD, PRD_SECCIONES, errores)

    # Regla: cada criterio de aceptacion debe ser medible.
    criterios = presentes.get(_normalizar("9. Criterios de aceptacion"), [])
    lista = items(criterios)
    if not lista:
        errores.append(f"{PRD}: 'Criterios de aceptacion' no tiene ningun item en lista")
    for c in lista:
        if not (TIENE_NUMERO.search(c) and TIENE_UNIDAD.search(c)):
            errores.append(
                f"{PRD}: criterio no verificable (falta metrica o umbral) -> {c!r}"
            )

    # Regla: el rollback es innegociable en un corte de canales.
    rollback = presentes.get(_normalizar("8. Plan de rollback"), [])
    if not items(rollback):
        errores.append(f"{PRD}: 'Plan de rollback' debe listar los pasos concretos de reversion")

    # Regla: canales afectados enumerados uno por uno.
    canales = presentes.get(_normalizar("2. Canales afectados"), [])
    if not items(canales):
        errores.append(f"{PRD}: 'Canales afectados' debe enumerar cada canal como item de lista")


def check_diseno(root, errores, warnings):
    texto_prd = leer(root, PRD)
    texto_arq = leer(root, ARQ)
    texto_guard = leer(root, GUARD)

    if texto_arq is None:
        errores.append(f"{ARQ}: no existe. Ejecuta /diseno para generarlo.")
    else:
        presentes = _chequear_doc(texto_arq, ARQ, ARQ_SECCIONES, errores)

        # Regla: el diseno tiene que tener al menos un diagrama versionado y existente.
        diag = presentes.get(_normalizar("7. Diagramas"), [])
        diagramas = re.findall(r"\(([^)]+\.mmd)\)", "\n".join(diag))
        if not diagramas:
            errores.append(f"{ARQ}: 'Diagramas' no referencia ningun archivo .mmd")
        for ref in diagramas:
            destino = os.path.normpath(os.path.join(root, os.path.dirname(ARQ), ref))
            if not os.path.isfile(destino):
                errores.append(f"{ARQ}: el diagrama referenciado no existe -> {ref}")

    if texto_guard is None:
        errores.append(f"{GUARD}: no existe. Sin guardarrailes no hay compuerta.")
    else:
        g = secciones(texto_guard)
        prohibido = items(g.get(_normalizar("Prohibido"), []))
        obligatorio = items(g.get(_normalizar("Obligatorio"), []))
        if len(prohibido) < 3:
            errores.append(
                f"{GUARD}: 'Prohibido' tiene {len(prohibido)} items, se requieren al menos 3"
            )
        if not obligatorio:
            errores.append(f"{GUARD}: 'Obligatorio' no tiene ningun item")
        frag = buscar_placeholder(texto_guard)
        if frag:
            errores.append(f"{GUARD}: sin completar -> {frag}")

    # Regla: toda decision marcada en el PRD necesita su ADR real.
    refs = set()
    if texto_prd is not None:
        decisiones = secciones(texto_prd).get(_normalizar("10. Decisiones que requieren ADR"), [])
        refs = set(ADR_REF.findall("\n".join(decisiones)))
        declaradas = items(decisiones)
        sin_ref = [d for d in declaradas if not ADR_REF.search(d)]
        for d in sin_ref:
            errores.append(f"{PRD}: decision sin ADR asociado -> {d!r}")
        if not declaradas:
            warnings.append(
                f"{PRD}: no se declaro ninguna decision que requiera ADR. "
                "Confirma que el diseno no tiene decisiones irreversibles."
            )
        for num in sorted(refs):
            _check_adr(root, num, errores)

    # Un ADR huerfano (existe pero nadie lo referencia) tambien es ruido.
    for ruta in sorted(glob.glob(os.path.join(root, ADR_DIR, "ADR-*.md"))):
        nombre = os.path.basename(ruta)
        if nombre.startswith("ADR-0000"):
            continue
        num = ADR_REF.search(nombre)
        if texto_prd is not None and num and num.group(1) not in refs:
            warnings.append(f"{ADR_DIR}/{nombre}: no esta referenciado desde el PRD")


def _check_adr(root, num, errores):
    patron = os.path.join(root, ADR_DIR, f"ADR-{num}-*.md")
    encontrados = glob.glob(patron)
    if not encontrados:
        errores.append(f"{ADR_DIR}: falta ADR-{num}-*.md, referenciado desde el PRD")
        return
    rel = os.path.relpath(encontrados[0], root).replace("\\", "/")
    with open(encontrados[0], encoding="utf-8") as fh:
        texto = fh.read()

    presentes = _chequear_doc(texto, rel, ADR_SECCIONES, errores)

    # Regla: un ADR sin alternativas descartadas es una decision no argumentada.
    alt = presentes.get(_normalizar("Alternativas descartadas"), [])
    if not any("por que no" in _normalizar(l) for l in alt):
        errores.append(
            f"{rel}: 'Alternativas descartadas' debe explicar al menos una con 'Por que no:'"
        )

    estado = " ".join(presentes.get(_normalizar("Estado"), [])).lower()
    if "aceptada" not in estado and "aceptado" not in estado:
        errores.append(f"{rel}: 'Estado' debe ser 'Aceptada' para poder implementar (actual: {estado.strip()!r})")


def run_checks(root, stage="all"):
    """Devuelve (errores, warnings). Usado por el CLI y por el hook."""
    errores, warnings = [], []
    if stage in ("1", "all"):
        check_requisitos(root, errores, warnings)
    if stage in ("2", "all"):
        check_diseno(root, errores, warnings)
    return errores, warnings


def main():
    ap = argparse.ArgumentParser(description="Valida la completitud de requisitos y diseno.")
    ap.add_argument("--stage", choices=["1", "2", "all"], default="all")
    ap.add_argument("--root", default=None, help="Raiz del proyecto (por defecto, la del script)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errores, warnings = run_checks(root, args.stage)

    for w in warnings:
        print(f"[WARN]  {w}")
    for e in errores:
        print(f"[ERROR] {e}")

    if errores:
        if not args.quiet:
            print(f"\nSpec incompleta: {len(errores)} error(es). No avanzar a implementacion.")
        return 1
    if not args.quiet:
        etapa = {"1": "Requisitos", "2": "Diseno", "all": "Requisitos + Diseno"}[args.stage]
        print(f"[OK] {etapa}: spec completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

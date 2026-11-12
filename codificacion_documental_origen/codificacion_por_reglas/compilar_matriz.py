#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compilar_matriz.py - Compila la matriz documental a partir de los JSON por sitio
producidos por codificar_documental.py y la compara con la matriz publicada.

Salidas (en la carpeta de resultados indicada):
  matriz_reglas.csv            matriz ancha, mismo formato de columnas que documentary_matrix.csv
  matriz_reglas_larga.csv      una fila por celda codificada
  acuerdo_por_indicador.csv    acuerdo observado y kappa de Cohen (4 categorías y binario)
  discrepancias.csv            celdas en que reglas y matriz publicada difieren, con evidencia,
                               para la conciliación humana
  informe_acuerdo.md           resumen legible, con la fecha y el modo de la corrida

Kappa de Cohen: acuerdo entre dos codificaciones corregido por el que se esperaría por azar.
Binario = «sí» frente a cualquier otro código, que es la agregación usada en el artículo.
Intervalo de confianza al 95 % por remuestreo de instituciones (bootstrap, 2000 réplicas,
semilla fija), de modo que el resultado es reproducible.

Uso (PowerShell):
    py compilar_matriz.py --resultados salida_vivo
    py compilar_matriz.py --resultados salida_wayback_20260811
"""
import argparse, csv, json, random, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

COLUMNAS = {
    "mundo": {"privacy_notice": "Not.", "legal_framework": "Frm.", "data_subject_rights": "Rts.",
              "dpo_contact": "DPO", "cookie_policy": "Ckp.", "accessibility_statement": "Acc."},
    "ecuador": {"privacy_notice": "Notice", "legal_framework": "LOPDP", "data_subject_rights": "Rights",
                "dpo_contact": "DPO", "accessibility_statement": "Acc.", "lotaip_transparency": "Transp."},
}
INDICADORES = ["privacy_notice", "legal_framework", "data_subject_rights", "dpo_contact",
               "cookie_policy", "accessibility_statement", "lotaip_transparency"]
CATS = ["si", "no", "parcial", "nv"]
B_REPLICAS, SEMILLA = 2000, 20261111


def kappa(pares, cats):
    n = len(pares)
    if n == 0:
        return None
    po = sum(a == b for a, b in pares) / n
    ca, cb = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum(ca[c] * cb[c] for c in cats) / (n * n)
    if pe == 1:
        return 1.0 if po == 1 else None
    return (po - pe) / (1 - pe)


def ic_bootstrap(pares, cats):
    rnd = random.Random(SEMILLA)
    vals = []
    for _ in range(B_REPLICAS):
        m = [pares[rnd.randrange(len(pares))] for _ in pares]
        k = kappa(m, cats)
        if k is not None:
            vals.append(k)
    if len(vals) < B_REPLICAS * 0.9:
        return None, None
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def leer_publicada(ruta):
    pub = {}
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            g, sig = r["grupo"], r["Abbr."]
            for ind, col in COLUMNAS[g].items():
                pub[(g, sig, ind)] = r[col].rstrip("*")
    return pub


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resultados", required=True, help="carpeta salida_<modo> de codificar_documental.py")
    ap.add_argument("--publicada", default="entrada/documentary_matrix_publicada.csv")
    a = ap.parse_args()
    res = Path(a.resultados)

    sitios = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((res / "sitios").glob("*.json"))]
    if not sitios:
        sys.exit(f"No hay resultados en {res / 'sitios'}")
    pub = leer_publicada(a.publicada)
    modos = sorted({s["modo"] for s in sitios})
    versiones = sorted({(s["version"], s["sha256_script"][:12]) for s in sitios})
    fechas = sorted(s["fecha_ejecucion_utc"] for s in sitios)

    # --- matriz ancha y larga ---
    filas_anchas, filas_largas = [], []
    for s in sitios:
        g = s["grupo"]
        fila = {"id": s["id"], "grupo": g, "Abbr.": s["sigla"], "C": s["pais"]}
        for ind, col in COLUMNAS[g].items():
            v = s["codigos"].get(ind, "")
            fila[col] = v
            filas_largas.append({"id": s["id"], "grupo": g, "abbr": s["sigla"], "indicador": ind,
                                 "columna": col, "valor_reglas": v,
                                 "valor_publicado": pub.get((g, s["sigla"], ind), "")})
        filas_anchas.append(fila)
    cols = ["id", "grupo", "Abbr.", "C"] + list(COLUMNAS["mundo"].values()) + \
           [c for c in COLUMNAS["ecuador"].values() if c not in COLUMNAS["mundo"].values()]
    with open(res / "matriz_reglas.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="no_aplica"); w.writeheader(); w.writerows(filas_anchas)
    with open(res / "matriz_reglas_larga.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas_largas[0])); w.writeheader(); w.writerows(filas_largas)

    # --- acuerdo ---
    por_ind = defaultdict(list)
    for r in filas_largas:
        if r["valor_reglas"] and r["valor_publicado"]:
            por_ind[(r["grupo"], r["indicador"])].append((r["valor_reglas"], r["valor_publicado"]))
            por_ind[("ambos", r["indicador"])].append((r["valor_reglas"], r["valor_publicado"]))
    filas_ac = []
    for (g, ind), pares in sorted(por_ind.items(), key=lambda x: (x[0][0], INDICADORES.index(x[0][1]))):
        bin_ = [(x == "si", y == "si") for x, y in pares]
        k4, kb = kappa(pares, CATS), kappa(bin_, [True, False])
        lo4, hi4 = ic_bootstrap(pares, CATS)
        lob, hib = ic_bootstrap(bin_, [True, False])
        f = lambda v: "" if v is None else f"{v:.3f}"
        filas_ac.append({"grupo": g, "indicador": ind, "n": len(pares),
                         "acuerdo_observado": f(sum(x == y for x, y in pares) / len(pares)),
                         "kappa_4cat": f(k4), "ic95_4cat": f"[{f(lo4)}, {f(hi4)}]",
                         "acuerdo_binario": f(sum(x == y for x, y in bin_) / len(bin_)),
                         "kappa_binario": f(kb), "ic95_binario": f"[{f(lob)}, {f(hib)}]",
                         "si_reglas": sum(x == "si" for x, _ in pares),
                         "si_publicada": sum(y == "si" for _, y in pares)})
    with open(res / "acuerdo_por_indicador.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas_ac[0])); w.writeheader(); w.writerows(filas_ac)

    # --- discrepancias con evidencia ---
    ev = {s["id"]: s["evidencia"] for s in sitios}
    disc = []
    for r in filas_largas:
        if r["valor_publicado"] and r["valor_reglas"] != r["valor_publicado"]:
            e = ev[r["id"]]
            disc.append(r | {"aviso_url": e.get("aviso_url") or "",
                             "coincidencias": json.dumps(e.get("coincidencias", {}), ensure_ascii=False)[:500],
                             "motivo_nv": e.get("motivo_nv", ""), "codigo_conciliado": "", "nota_conciliacion": ""})
    with open(res / "discrepancias.csv", "w", encoding="utf-8-sig", newline="") as f:
        campos = list(filas_largas[0]) + ["aviso_url", "coincidencias", "motivo_nv",
                                          "codigo_conciliado", "nota_conciliacion"]
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(disc)

    # --- informe ---
    L = ["# Acuerdo entre la codificación por reglas y la matriz publicada", "",
         f"- Modo de recuperación: {', '.join(modos)}",
         f"- Script: codificar_documental.py, versión(es) {versiones}",
         f"- Ejecución (UTC): {fechas[0]} a {fechas[-1]}",
         f"- Compilación (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
         f"- Instituciones: {len(sitios)}; celdas comparadas: {sum(len(v) for k, v in por_ind.items() if k[0] != 'ambos')}",
         f"- Celdas discrepantes: {len(disc)} (detalle en discrepancias.csv)", "",
         "Esta codificación se ejecutó después de la publicación de la matriz y con un instrumento",
         "distinto. Una discrepancia puede deberse a un error de la matriz, a una limitación de las",
         "reglas o a un cambio del sitio entre agosto de 2026 y la fecha de la corrida.", "",
         "| Grupo | Indicador | n | Acuerdo | κ (4 cat.) [IC95] | Acuerdo bin. | κ binario [IC95] | Sí reglas | Sí publicada |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in filas_ac:
        L.append(f"| {r['grupo']} | {r['indicador']} | {r['n']} | {r['acuerdo_observado']} | {r['kappa_4cat']} {r['ic95_4cat']} | "
                 f"{r['acuerdo_binario']} | {r['kappa_binario']} {r['ic95_binario']} | {r['si_reglas']} | {r['si_publicada']} |")
    (res / "informe_acuerdo.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()

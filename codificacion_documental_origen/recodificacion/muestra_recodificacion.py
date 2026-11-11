# -*- coding: utf-8 -*-
"""Muestra aleatoria para la doble codificacion documental independiente.

15 instituciones de cada grupo, semilla fija 20261111, a partir del censo
data/raw/census/universities.json. Genera una hoja en blanco por codificador.
Uso: python muestra_recodificacion.py ruta/universities.json
"""
import csv, json, random, sys
U = json.load(open(sys.argv[1], encoding="utf-8"))
rng = random.Random(20261111)
muestra = []
for g in sorted({u["grupo"] for u in U}):
    pool = sorted([u for u in U if u["grupo"] == g], key=lambda u: u["id"])
    muestra += sorted(rng.sample(pool, 15), key=lambda u: u["id"])
cols = ["id", "grupo", "sigla", "nombre", "url",
        "aviso_privacidad", "marco_normativo", "derechos", "contacto_dpo",
        "declaracion_accesibilidad", "url_aviso_consultado", "fecha_hora", "nota"]
for cod in ("A", "B"):
    with open(f"hoja_codificador_{cod}.csv", "w", newline="", encoding="utf-8-sig") as h:
        w = csv.writer(h, delimiter=";"); w.writerow(cols)
        for u in muestra:
            w.writerow([u["id"], u["grupo"], u["sigla"], u["nombre"], u["url"]] + [""] * 8)
print(len(muestra), "instituciones:", ", ".join(u["sigla"] for u in muestra))

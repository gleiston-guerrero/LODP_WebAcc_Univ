# Hallazgos — Privacidad de datos en sitios web de IES del Ecuador

Análisis realizado el 2026-08-11. Censo de **63 IES** registradas en SENESCYT/CES
(35 públicas, 8 cofinanciadas, 20 autofinanciadas). Método: recuperación automatizada
de sitios (no ejecuta JavaScript → los banners de cookies quedan subestimados).

## Entregables en el proyecto
- `claude/privacidad_ies.tex` — sección del manuscrito (LaTeX autónomo, compila con pdflatex→bibtex→pdflatex×2).
- `claude/privacidad_ies.bib` — 18 referencias (15 académicas Q1/Q2 + venues top verificadas contra Crossref; 3 fuentes legales: LOPDP 2021, Reglamento D.E. 904/2023, RGPD 2016).
- Matriz Excel `privacidad_ies_ecuador.xlsx` (entregada en el chat; la carga al proyecto falló por formato binario). Hoja "Matriz" (63×17) + hoja "Resumen" con fórmulas.

## Resultados clave (n=63)
- Política de privacidad/aviso de tratamiento: 39/63 (61.9%).
- Menciona expresamente la LOPDP: 31/63 (49.2%).
- Enumera derechos del titular: 35/63 (55.6%).
- Designa DPO/contacto de datos: 24/63 (38.1%).
- Banner de cookies confirmado: 6/63 (9.5%) — subestimado por el método.
- Política de cookies: 15/63 (23.8%).
- Acción afirmativa/accesibilidad web: 7/63 (11.1%).
- Transparencia/LOTAIP: 47/63 (74.6%; 34/35 públicas vs 7/20 autofinanciadas).
- Certificado TLS válido: 58/63 (92.1%). Deficientes: ESPAM MFL, UTA, Yachay Tech, U. Otavalo, UTB (subdominio www).

## Patrones problemáticos detectados
1. Bases legales erróneas/obsoletas: UTE, UNIANDES, UTI (Ley de Comercio Electrónico / Registro de Datos Públicos); UNIB.E (GDPR/CCPA en vez de LOPDP).
2. Alcance acotado (solo app móvil / admisión / posgrado): UTN, UTEQ, UPSE.
3. Ausencia total de instrumentos: UNL, UAgraria, UTM, UNAE, ULVR, UDA, UDR, UDET, entre otros.

## Casos de referencia (marco más completo y verificable)
UNACH, ESPE, UASB, ESPOL, UG, UTMACH, Ikiam, UArtes (públicas); PUCE, UCSG, UCACUE, UTPL (cofinanciadas);
UIDE, UEES, UDLA, USFQ, Casa Grande, UTEG, USGP, U. Hemisferios, ECOTEC, UBE (autofinanciadas).

## Limitaciones del método (declaradas en el manuscrito)
- No ejecuta JS → cookies subestimadas.
- Sitios que bloquean acceso (WAF/robots) o PDFs en imagen → marcados "no verificable" (UISRAEL, UMET, U. Pacífico, U. Otavalo, UTA por certificado).
- Solo evalúa lo publicado, no las prácticas internas de tratamiento.

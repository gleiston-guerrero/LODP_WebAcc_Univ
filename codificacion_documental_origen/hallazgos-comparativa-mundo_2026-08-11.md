# Hallazgos — Comparativa mundo vs Ecuador (privacidad web universitaria)

Análisis 2026-08-11. Se replicó el estudio de Ecuador sobre las **63 mejores universidades del mundo**
(consenso QS 2026 + THE 2026 + ARWU 2025), con la dimensión legal adaptada a cada jurisdicción.
Mismo método (WebFetch/WebSearch, no ejecuta JS → banners de cookies subestimados por igual en ambos grupos).

## Selección (consenso)
Top 75 de cada ranking → rango promedio (ausencia del top-75 = puesto 76), priorizando presencia en los 3 rankings:
46 presentes en los tres + 17 mejores presentes en dos = 63. Corte en U. Queensland (LSE primera excluida).
Distribución: EE.UU. 24, Europa cont. 10, Reino Unido 7, China 6, Australia 5, Asia (otros) 5, HK 3, Canadá 3.
Detalle con puestos en `claude/seleccion63-mundo.json`.

## Entregables en el proyecto
- `claude/privacidad_mundo.tex` — sección comparativa (LaTeX autónomo).
- `claude/privacidad_mundo.bib` — 23 entradas (incluye Degeling 2019 NDSS, Kretschmer 2021 ACM TWEB y las 3 fuentes de rankings).
- Excel `privacidad_mundo_vs_ecuador.xlsx` (entregado en el chat): hojas Matriz Mundo, Resumen Mundo (por región), Ecuador (ref) y Comparativa.

## Comparativa (Sí sobre 63 en cada grupo)
| Indicador | Mundo | Ecuador |
|---|---|---|
| Política de privacidad | 58 (92.1%) | 39 (61.9%) |
| Marco legal citado | 48 (76.2%) | 31 (49.2%) |
| Derechos del interesado | 47 (74.6%) | 35 (55.6%) |
| DPO / contacto de datos | 54 (85.7%) | 24 (38.1%) |
| Banner de cookies (confirmado) | 4 (6.3%) | 6 (9.5%) |
| Política de cookies | 14 (22.2%) | 15 (23.8%) |
| Accesibilidad / inclusión | 47 (74.6%) | 7 (11.1%) |
| Certificado TLS válido | 63 (100%) | 58 (92.1%) |

## Conclusiones clave
- Brechas mayores y robustas (documentos estáticos, no dependen de JS): **DPO** (85.7% vs 38.1%) y **accesibilidad** (74.6% vs 11.1%), además de política de privacidad y marco legal.
- **Cookies**: el banner confirmado NO es comparable (subdetección por JS, mayor en el grupo mundial sujeto a RGPD/ePrivacy). La política de cookies documental sí es comparable y es similar (~22-24% en ambos).
- Regional: Europa cont. lidera marco legal (9/10 GDPR); EE.UU. lidera accesibilidad (22/24, ADA); China es el rezagado del grupo élite (marco 2/6, accesibilidad 0/6; Fudan y SJTU sin política central).
- El referente mundial no es perfecto: Harvard, Michigan, WUSTL sin derechos/marco en el aviso principal; banners de élite a menudo incumplen consentimiento libre (Nouwens 2020, Gray 2021).
- Hoja de ruta para Ecuador: política anclada en LOPDP+Reglamento, DPO/canal visible, y accesibilidad WCAG.

# Two barriers to equitable access: manuscrito

Manuscrito *Two barriers to equitable access: WCAG conformance and pre-consent tracking on Ecuadorian and top-ranked university websites*, preparado primero para *Universal Access in the Information Society* (Springer Nature) y adaptado después a *Behaviour & Information Technology* (Taylor & Francis), que es la revista de destino actual. La versión vigente para el envío está en `envio_BIT/`.

Autores: Gleiston Guerrero-Ulloa (UTEQ), Andrea Zúñiga Paredes (Ministerio de Educación del Ecuador) y Efraín Díaz-Macías (UTEQ).

## Alcance de este directorio

Aquí se versiona **únicamente el contenido del manuscrito**: los archivos `.tex` principales, la bibliografía, las figuras en el formato en que entran a la compilación, la plantilla de la revista y los PDF compilados.

**No se versiona aquí**, y no debe copiarse aquí:

- datos brutos ni derivados de la auditoría,
- código de recolección ni de análisis,
- el libro de códigos,
- salidas intermedias de compilación (`.aux`, `.log`, `.out`, `.blg`, `.toc`, `.synctex.gz`).

Todo lo que sustenta las cifras vive en el depósito citable [10.5281/zenodo.22405998](https://doi.org/10.5281/zenodo.22405998), espejado en [`wcag-preconsent-tracking-university-websites`](https://github.com/gleiston-guerrero/wcag-preconsent-tracking-university-websites). Ese depósito es la fuente de registro de cualquier cifra del artículo; este directorio es la fuente de registro del texto que las reporta.

Cuando una cifra cambie, cambia primero en el depósito y después aquí, nunca al revés.

## Contenido

| Archivo | Qué es |
|---|---|
| `privacidad_UAIS_en.tex` | Manuscrito en inglés, **archivo principal** de la versión que se envía a la revista |
| `privacidad_UAIS_es.tex` | Versión en español del mismo manuscrito, con las mismas cifras |
| `privacidad_mundo.bib` | Bibliografía (BibTeX) que usan ambas versiones |
| `privacidad_UAIS_en.bbl`, `privacidad_UAIS_es.bbl` | Bibliografía ya procesada; permite compilar sin ejecutar BibTeX |
| `fig_cookies.pdf`, `fig_countries.pdf`, `fig_forest.pdf`, `fig_timeline.pdf`, `fig_vantage.pdf`, `fig_wcag_levels.pdf` | Las seis figuras, generadas por `code/analysis/figures_uais.py` y `fig_vantage.py` del depósito |
| `sn-jnl.cls`, `sn-basic.bst` | Plantilla y estilo bibliográfico de Springer Nature |
| `privacidad_UAIS_en.pdf`, `privacidad_UAIS_es.pdf` | PDF compilados de ambas versiones |
| `envio_revista/cover_letter_UAIS.tex`, `envio_revista/cover_letter_UAIS.pdf` | Carta de presentación para el envío |
| `envio_revista/UAIS_submission_LaTeX.zip` | Paquete LaTeX que se envía a la revista: versión en inglés, `.bib`, `.bbl`, plantilla y figuras en una sola carpeta, con `README.txt` de compilación |
| `envio_BIT/privacidad_BIT.tex` | **Versión vigente** para *Behaviour & Information Technology*: plantilla Interact de Taylor & Francis con referencias APA 7, autores y todas las declaraciones |
| `envio_BIT/privacidad_BIT_anonymised.tex` | Versión anónima para la revisión doble anónima; solo activa `\anonversion` y carga `privacidad_BIT.tex`, así que el texto es idéntico |
| `envio_BIT/privacidad_mundo_BIT.bib` | Bibliografía de la versión para Taylor & Francis (mismas referencias, mayúsculas protegidas para el estilo APA) |
| `envio_BIT/interact.cls`, `envio_BIT/tfapastyle.sty`, `envio_BIT/tfapacite.bst` | Plantilla y estilo bibliográfico de Taylor & Francis |
| `envio_BIT/privacidad_BIT.pdf`, `envio_BIT/privacidad_BIT_anonymised.pdf` | PDF compilados (46 y 45 páginas, A4) |
| `envio_BIT/BIT_submission_LaTeX.zip` | Paquete LaTeX autocontenido para subir a la revista, con su `README.txt` |
| `informe_revision_UAIS_dos_barreras.tex` | Informe de revisión por pares del manuscrito, en español; no forma parte de la compilación |

## Compilación de la versión vigente (Behaviour & Information Technology)

Desde la carpeta `envio_BIT` (Windows, PowerShell o símbolo del sistema):

```bat
cd envio_BIT
pdflatex privacidad_BIT_anonymised.tex
bibtex privacidad_BIT_anonymised
pdflatex privacidad_BIT_anonymised.tex
pdflatex privacidad_BIT_anonymised.tex
```

Para la versión completa, sustituya `privacidad_BIT_anonymised` por `privacidad_BIT`. Resultado esperado: 45 y 46 páginas en A4, sin citas ni referencias sin resolver. BibTeX muestra avisos de pila del estilo `tfapacite.bst` que no alteran la lista de referencias (detalle en `envio_BIT/README.txt`).

## Compilación de la versión para UAIS (archivada)

Requisitos: una distribución LaTeX con `pdflatex` y `bibtex` (TeX Live 2023 o posterior, o MiKTeX). La clase `sn-jnl.cls` y el estilo `sn-basic.bst` están incluidos, así que no hay que instalar la plantilla de la revista.

- Compilador: **pdfLaTeX**
- Archivo principal: **`privacidad_UAIS_en.tex`** (la versión en español, `privacidad_UAIS_es.tex`, se compila igual)
- Bibliografía: **BibTeX**, con `privacidad_mundo.bib` y `sn-basic.bst`

Orden de comandos (Windows, PowerShell o símbolo del sistema, desde la carpeta del repositorio):

```bat
git clone https://github.com/gleiston-guerrero/LODP_WebAcc_Univ.git
cd LODP_WebAcc_Univ
pdflatex privacidad_UAIS_en.tex
bibtex privacidad_UAIS_en
pdflatex privacidad_UAIS_en.tex
pdflatex privacidad_UAIS_en.tex
```

Para la versión en español, sustituya `privacidad_UAIS_en` por `privacidad_UAIS_es`.

Resultado esperado: `privacidad_UAIS_en.pdf` de 40 páginas y `privacidad_UAIS_es.pdf` de 43 páginas, ambos en tamaño A4, sin citas ni referencias sin resolver. Las advertencias de sustitución de tamaño de fuente que aparecen en el registro provienen de la plantilla y no afectan al resultado.

Two barriers to equitable access: WCAG conformance and pre-consent tracking
on Ecuadorian and top-ranked university websites

Manuscript submitted to Universal Access in the Information Society
Corresponding author: Gleiston Guerrero-Ulloa (gguerrero@uteq.edu.ec)


CONTENTS

  privacidad_UAIS_en.tex     main file of the manuscript
  privacidad_mundo.bib       bibliography database (BibTeX)
  privacidad_UAIS_en.bbl     processed bibliography; allows compilation without BibTeX
  sn-jnl.cls                 Springer Nature journal class
  sn-basic.bst               Springer Nature basic reference style (numbered)
  fig_forest.pdf             Figure 1
  fig_cookies.pdf            Figure 2
  fig_wcag_levels.pdf        Figure 3
  fig_vantage.pdf            Figure 4
  fig_countries.pdf          Figure E1 (Appendix E)
  fig_timeline.pdf           Figure E2 (Appendix E)

All files are in a single folder; there are no subfolders and no external
inputs. Figures are vector PDF files.


COMPILATION

  Engine:     pdfLaTeX (TeX Live 2023 or later, or MiKTeX)
  Main file:  privacidad_UAIS_en.tex
  References: BibTeX with sn-basic.bst

  pdflatex privacidad_UAIS_en.tex
  bibtex   privacidad_UAIS_en
  pdflatex privacidad_UAIS_en.tex
  pdflatex privacidad_UAIS_en.tex

If BibTeX is not run, the included privacidad_UAIS_en.bbl is used and the
result is identical.

Expected output: privacidad_UAIS_en.pdf, A4, 39 pages, with no undefined
citations or references.


DATA AND CODE

The data and analysis code behind every figure are deposited at
https://doi.org/10.5281/zenodo.22405998

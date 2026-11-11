Two barriers to equitable access: WCAG conformance and pre-consent tracking
on Ecuadorian and top-ranked university websites

Manuscript prepared for Behaviour & Information Technology (Taylor & Francis)
Template: Interact layout with APA 7 references (interact.cls, tfapastyle.sty,
tfapacite.bst), downloaded from Taylor & Francis.


TWO VERSIONS FROM ONE SOURCE

  privacidad_BIT_anonymised.tex   anonymised manuscript for double-anonymised
                                  review: no author names, affiliations or
                                  identifying declarations; the DOI of the data
                                  deposit is withheld
  privacidad_BIT.tex              full version with authors, affiliations and
                                  all declarations

The anonymised file only sets \anonversion to 1 and inputs privacidad_BIT.tex,
so the text of both versions is identical.


CONTENTS

  privacidad_BIT.tex, privacidad_BIT_anonymised.tex   main files
  privacidad_mundo_BIT.bib                            bibliography (BibTeX)
  privacidad_BIT.bbl, privacidad_BIT_anonymised.bbl   processed bibliography;
                                                      allows compilation
                                                      without BibTeX
  interact.cls, tfapastyle.sty, tfapacite.bst         Taylor & Francis template
  fig_forest.pdf        Figure 1
  fig_cookies.pdf       Figure 2
  fig_wcag_levels.pdf   Figure 3
  fig_vantage.pdf       Figure 4
  fig_countries.pdf     Figure E1 (Appendix E)
  fig_timeline.pdf      Figure E2 (Appendix E)

All files are in a single folder, with no subfolders and no external inputs.


COMPILATION

  Engine:     pdfLaTeX (TeX Live 2023 or later, or MiKTeX)
  References: BibTeX with tfapacite.bst

  pdflatex privacidad_BIT_anonymised.tex
  bibtex   privacidad_BIT_anonymised
  pdflatex privacidad_BIT_anonymised.tex
  pdflatex privacidad_BIT_anonymised.tex

  (same sequence with privacidad_BIT for the full version)

Expected output: A4, single column; privacidad_BIT_anonymised.pdf 47 pages,
privacidad_BIT.pdf 48 pages; no undefined citations or references.

Note on tfapacite.bst: the distributed file calls the function
format.author.names before defining it. In this copy the definition of
format.editors.as.authors.no.postfix was moved below format.author.names;
nothing else was changed. BibTeX still prints "literal stack isn't empty"
messages while sorting; they do not alter the reference list.


DATA AND CODE

https://doi.org/10.5281/zenodo.22405998

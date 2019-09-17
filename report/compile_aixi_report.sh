#!/bin/sh

pandoc --standalone \
--listings \
--metadata-file=./pandoc_latex.yml \
--pdf-engine=xelatex \
--template eisvogel \
--filter pandoc-fignos \
--filter pandoc-eqnos \
--filter pandoc-tablenos \
--filter pandoc-crossref \
--filter pandoc-citeproc \
--filter pandoc-asciimath \
--output=aixi_report.pdf \
--toc -N \
aixi_report.md

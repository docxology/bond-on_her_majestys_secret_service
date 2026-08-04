# Manuscript — PIZ GLORIA (on_her_majestys_secret_service)

This directory holds the manuscript for the mission software package. The
paper identity is *On Her Majesty's Secret Service: PIZ GLORIA — Special-Agent
Mission Software*.

## Files

* `00_abstract.md` .. `07_scope_and_related_work.md` — numbered prose sections
  (token-hydrated; the only files the live cross-reference gate scans).
* `99_references.md` — bibliography.
* `config.yaml` — paper metadata, mission scenario, render toggles.
* `config.yaml.example` — reference copy of every configurable field.
* `layer_contract.yaml` — layer boundaries (domain / adapter / scripts).
* `SYNTAX.md` — Pandoc cross-reference and figure syntax.
* `references.bib` — BibTeX bibliography (mirrors `99_references.md`).
* `preamble.md` — LaTeX injections shared by PDF output.

## Token protocol

Measured values are injected as `{{TOKEN}}`s from
`src/on_her_majestys_secret_service/manuscript_variables.py`, never
hand-authored. Run `scripts/z_generate_manuscript_variables.py` to hydrate.

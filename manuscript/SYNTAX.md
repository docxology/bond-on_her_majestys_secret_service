# SYNTAX — PIZ GLORIA manuscript syntax reference

## Cross-references

Use Pandoc-crossref syntax; never hardcoded numbers.

* Narrative: `@sec:methodology`, `@fig:dispersion`
* Parenthetical: `[@sec:results]`, `[@fig:dispersion]`

Section labels live in `{#sec:...}` headers; figure labels on the image line.

## Figures

```markdown
![Ground-level centreline aerosol concentration along the plume axis.](../output/figures/aerosol_plume.png){#fig:dispersion}
```

## Tokens

Measured values are injected as `{{TOKEN}}` (e.g. `{{PIZ_ISOPLETH_REACH_M}}`).
The authoritative set is the return of
`generate_variables()`; the live test
`tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
gates it. Keep prose metrics tokenized.

## Citations

BibTeX keys from `references.bib` via `@key` / `[@key]` syntax (Pandoc).

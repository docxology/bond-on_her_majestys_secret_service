# Manifest — PIZ GLORIA (on_her_majestys_secret_service)

## Token protocol

Measured mission values must use `{{TOKEN}}` syntax so they cannot drift from
the code; they resolve through
`src/on_her_majestys_secret_service/manuscript_variables.py::generate_variables`.

Pipeline:
1. `scripts/z_generate_manuscript_variables.py` calls `generate_variables()`
2. writes `output/data/manuscript_variables.json`
3. copies each `manuscript/[0-9]*.md` to `output/manuscript/`, substituting
   every `{{TOKEN}}`; strict mode fails on leftovers.

Adding a token: add the key to `generate_variables()`, use it in a section,
and the live cross-reference test in `tests/test_manuscript_variables.py`
enforces the mapping.

## Figure protocol

Figures are referenced via Pandoc-crossref labels. Current figure:

| Label | PNG | Generator |
| --- | --- | --- |
| `{#fig:dispersion}` | `output/figures/aerosol_plume.png` | `figures/dispersion.render_dispersion_figure` |

Add figures by adding a generator in `src/.../figures/`, wiring it into a
script, and referencing it `@fig:label` in a section.

## Editions

Edit sections in place, keeping measured numbers tokenized. The default
`manuscript/config.yaml` is authoritative for identity and scenario.

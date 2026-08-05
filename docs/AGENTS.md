# AGENTS.md — docs/ (PIZ GLORIA)

This file is the agent-facing contract for the `docs/` directory itself: what
lives here, who owns each file, and when an agent touching `src/`,
`manuscript/`, or the mission protocol must also touch `docs/`. It complements
— it does not replace — the package-root `AGENTS.md`, which is the
authoritative scope/quality-gate contract for the whole package.

## What's in this directory

| File | Owns | Update when |
| --- | --- | --- |
| `README.md` | Index of this directory | A file is added to or removed from `docs/` |
| `agent_instructions.md` | Hard operational rules (scope, determinism, no-mocks, coverage, layer contract, protocol stability) | A guardrail changes at the package-root `AGENTS.md` level — keep the two in sync |
| `architecture.md` | The real module graph: every file under `src/on_her_majestys_secret_service/`, what it computes, and the dependency direction between domain / adapter / presentation / scripts | A module is added, renamed, or its dependency edges change |
| `testing_philosophy.md` | Per-module test-suite intent (what each `test_*.py` file actually asserts, not just its name) | A test file is added, split, or its coverage focus changes |
| `_generated/COUNTS.md` | Live test count + coverage percentage | **Never hand-edit.** Regenerate the numbers by running the gate below and pasting the real output |
| `AGENTS.md` | This file | The directory's own file list or ownership rules change |

## The rule this directory exists to enforce

Documentation drift is a defect, not a style issue. If Phase 4 (or any later
change) adds a module to `src/`, that module is not "done" until:

1. `architecture.md` names it, in the layer it actually belongs to, with what
   it computes.
2. `manuscript/layer_contract.yaml` lists it under the correct layer
   (`domain`, `adapter`, `presentation`, or `orchestrators`).
3. The package-root `README.md` module table and `AGENTS.md` module count
   mention it.
4. `_generated/COUNTS.md` reflects a coverage run taken *after* the module's
   tests exist — never a stale number carried over from before the change.

An agent that adds a `src/` module and stops without touching this list has
left the package half-updated.

## Regenerating `_generated/COUNTS.md`

```bash
uv run python -m pytest tests/ --cov=src --cov-fail-under=90 -q
```

Copy the real "X passed" count and the real `TOTAL` coverage percentage from
that output into `_generated/COUNTS.md`. Do not compute, estimate, or carry
forward a number you have not just measured in this environment.

## Cross-references

* Package-root guardrails (scope, local-only, no mocks, protocol stability):
  `../AGENTS.md`.
* Manuscript token/figure protocol: `../manuscript/AGENTS.md`.
* Fleet-level rules this package must satisfy: `../../SCOPE.md` §5 (Quality
  Bar) and §7 (Verification).

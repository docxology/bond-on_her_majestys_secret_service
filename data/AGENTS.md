# data/ — the claim ledger

`claim_ledger.yaml` records the package's claims and what supports each one.

## Rules

- **One record per claim.** A claim without a ledger record is not part of the package's
  results; add the support before adding the claim.
- **Copy measured numbers from `docs/_generated/COUNTS.md`**, which the regeneration scripts
  write, rather than into prose or into a ledger by hand.
- **The ledger is a declaration, not a result.** It says what is claimed and on what basis; it
  does not make the claim true, and a generated count is not a verification.
- **Deterministic.** Nothing here may depend on wall-clock time or an untracked random draw.

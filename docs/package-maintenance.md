# Verify the vendored BOND-API dependency

This checkout is `on_her_majestys_secret_service` 0.1.0. The declared Python
range is `>=3.11`; [`.python-version`](../.python-version) selects
Python 3.15 for the checkout.

This checkout delegates its software interface to a recorded BOND-API copy.
[`pyproject.toml`](../pyproject.toml) points to [`vendor/bond-api/`](../vendor/bond-api/),
and [`PROVENANCE.json`](../vendor/bond-api/PROVENANCE.json) records the upstream
revision and checksums. The [vendor notes](../vendor/bond-api/VENDOR.md)
describe the provenance record.

From the project root with Python 3.11 or later, verify the dependency record:

```sh
python scripts/vendor.py --check
```

The check compares the recorded and present files and returns a nonzero
status if it detects drift. The [provenance test](../tests/test_vendor_provenance.py)
exercises the same command.

With Lychee installed, check local documentation navigation:

```sh
git diff --check
lychee --offline README.md AGENTS.md 'docs/**/*.md'
```

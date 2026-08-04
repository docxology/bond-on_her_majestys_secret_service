"""Tests for manuscript token hydration for PIZ GLORIA."""

from __future__ import annotations

from pathlib import Path

import pytest

from on_her_majestys_secret_service.manuscript_variables import (
    _TOKEN_RE,
    generate_variables,
    load_manuscript_config,
    resolve_manuscript_tree,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class TestLoadConfig:
    def test_loads_default_config(self) -> None:
        config = load_manuscript_config()
        assert config["paper"]["title"]
        assert isinstance(config["paper"], dict)

    def test_missing_config_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_manuscript_config(tmp_path / "nope.yaml")

    def test_invalid_config_type_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("- 1\n- 2\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_manuscript_config(bad)


class TestGenerateVariables:
    def test_returns_expected_tokens(self) -> None:
        variables = generate_variables()
        for token in (
            "BOND_FILM",
            "BOND_CODENAME",
            "BOND_VERSION",
            "BOND_TITLE",
            "BOND_SUBTITLE",
            "PIZ_ISOPLETH_REACH_M",
            "PIZ_PEAK_CONCENTRATION",
            "PIZ_PEAK_DISTANCE_M",
            "PIZ_ROUTE_DISTANCE_M",
            "PIZ_ROUTE_MEAN_GRADE_DEG",
            "PIZ_ROUTE_SAFE",
            "PIZ_BRAY_SCORE",
            "PIZ_BRAY_VERDICT",
            "PYTHON_VERSION",
            "NUMPY_VERSION",
            "GENERATION_TIMESTAMP",
        ):
            assert token in variables

    def test_strict_mode_produces_real_values(self) -> None:
        variables = generate_variables()
        assert variables["PIZ_ISOPLETH_REACH_M"] != "N/A"
        assert variables["PIZ_ROUTE_SAFE"] in {"safe", "unsafe"}
        assert variables["PIZ_BRAY_VERDICT"] in {"low", "medium", "high", "critical"}

    def test_draft_mode_allows_na(self, tmp_path: Path) -> None:
        variables = generate_variables(require_outputs=False)
        assert variables["PIZ_ISOPLETH_REACH_M"] == "N/A"

    def test_values_are_deterministic(self) -> None:
        a = generate_variables()
        b = generate_variables()
        # Timestamp may legitimately differ; the science tokens must not.
        for key in ("PIZ_ISOPLETH_REACH_M", "PIZ_ROUTE_DISTANCE_M", "PIZ_BRAY_SCORE"):
            assert a[key] == b[key]


class TestResolveTree:
    def test_resolves_into_output_dir(self, tmp_path: Path) -> None:
        out = tmp_path / "out"
        variables = generate_variables(require_outputs=False)
        resolved_dir, names = resolve_manuscript_tree(
            variables,
            manuscript_dir=PACKAGE_ROOT / "manuscript",
            output_dir=out,
            strict=False,
        )
        assert resolved_dir == out
        assert names
        for name in names:
            text = (out / name).read_text(encoding="utf-8")
            assert "{{" not in text

    def test_strict_mode_fails_on_unresolved_token(self, tmp_path: Path) -> None:
        # A synthetic manuscript with an unknown token must fail strict resolution.
        md = tmp_path / "manuscript"
        md.mkdir()
        (md / "01_bogus.md").write_text("value is {{NOT_A_TOKEN}}\n", encoding="utf-8")
        with pytest.raises(ValueError):
            resolve_manuscript_tree({"KNOWN": "x"}, manuscript_dir=md, output_dir=tmp_path / "o", strict=True)


class TestLiveCrossReference:
    """The gate: every {{TOKEN}} in manuscript prose sections is generated."""

    def test_all_manuscript_tokens_are_generated(self) -> None:
        variables = generate_variables()
        manuscript_dir = PACKAGE_ROOT / "manuscript"
        tokens: set[str] = set()
        for source in manuscript_dir.glob("[0-9][0-9]_*.md"):
            text = source.read_text(encoding="utf-8")
            tokens.update(match[2:-2] for match in _TOKEN_RE.findall(text))
        missing = sorted(tokens - set(variables))
        assert not missing, f"manuscript tokens not generated: {missing}"

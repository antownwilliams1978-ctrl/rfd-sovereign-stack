"""Tests for package-native and compatibility entrypoints."""

from pathlib import Path
from unittest.mock import patch, Mock
import importlib
import sys
import types


def test_legacy_dash_wrapper_calls_package_main():
    """Legacy sebek_dash.py should delegate to sebek.dashboard.main."""
    fake_dashboard = types.ModuleType("sebek.dashboard")
    fake_dashboard.main = Mock()
    original = sys.modules.get("sebek.dashboard")
    try:
        sys.modules["sebek.dashboard"] = fake_dashboard
        sebek_dash = importlib.import_module("sebek_dash")
        sebek_dash.main()
        fake_dashboard.main.assert_called_once()
    finally:
        if original is not None:
            sys.modules["sebek.dashboard"] = original
        else:
            sys.modules.pop("sebek.dashboard", None)


def test_legacy_speech_wrapper_calls_package_main():
    """Legacy sebek_speech_agent.py should delegate to sebek.speech.agent.main."""
    import sebek_speech_agent

    with patch("sebek_speech_agent.speech_main", return_value=0) as mock_main:
        rc = sebek_speech_agent.main()
        assert rc == 0
        mock_main.assert_called_once()


def test_legacy_mass_digest_wrapper_calls_package_main():
    """Legacy sebek_mass_digest.py should delegate to sebek.ingestion_cli.main."""
    import sebek_mass_digest

    with patch("sebek_mass_digest.ingestion_main", return_value=0) as mock_main:
        rc = sebek_mass_digest.main()
        assert rc == 0
        mock_main.assert_called_once()


def test_pyproject_discovers_sebek_subpackages():
    """Packaging config should include sebek subpackages for editable installs."""
    import tomllib

    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    includes = (
        data.get("tool", {})
        .get("setuptools", {})
        .get("packages", {})
        .get("find", {})
        .get("include", [])
    )
    assert "sebek*" in includes

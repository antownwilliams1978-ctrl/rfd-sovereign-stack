"""Tests for package-native and compatibility entrypoints."""

from pathlib import Path
from unittest.mock import patch


def test_legacy_dash_wrapper_calls_package_main():
    """Legacy sebek_dash.py should delegate to sebek.dashboard.main."""
    import sebek_dash

    with patch("sebek_dash.dashboard_main") as mock_main:
        sebek_dash.main()
        mock_main.assert_called_once()


def test_legacy_speech_wrapper_calls_package_main():
    """Legacy sebek_speech_agent.py should delegate to sebek.speech.agent.main."""
    import sebek_speech_agent

    with patch("sebek_speech_agent.speech_main", return_value=0) as mock_main:
        rc = sebek_speech_agent.main()
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

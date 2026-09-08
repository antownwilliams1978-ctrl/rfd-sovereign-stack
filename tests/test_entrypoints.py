"""Tests for package-native and compatibility entrypoints."""

from pathlib import Path
from unittest.mock import Mock
import importlib
import sys
import types
import tomllib


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
    fake_agent = types.ModuleType("sebek.speech.agent")
    fake_agent.main = Mock(return_value=0)
    original = sys.modules.get("sebek.speech.agent")
    try:
        sys.modules["sebek.speech.agent"] = fake_agent
        import sebek_speech_agent
        rc = sebek_speech_agent.main()
        assert rc == 0
        fake_agent.main.assert_called_once()
    finally:
        if original is not None:
            sys.modules["sebek.speech.agent"] = original
        else:
            sys.modules.pop("sebek.speech.agent", None)


def test_legacy_mass_digest_wrapper_calls_package_main():
    """Legacy sebek_mass_digest.py should delegate to sebek.ingestion_cli.main."""
    fake_ingestion = types.ModuleType("sebek.ingestion_cli")
    fake_ingestion.main = Mock(return_value=0)
    original = sys.modules.get("sebek.ingestion_cli")
    try:
        sys.modules["sebek.ingestion_cli"] = fake_ingestion
        import sebek_mass_digest
        rc = sebek_mass_digest.main()
        assert rc == 0
        fake_ingestion.main.assert_called_once()
    finally:
        if original is not None:
            sys.modules["sebek.ingestion_cli"] = original
        else:
            sys.modules.pop("sebek.ingestion_cli", None)


def test_pyproject_discovers_sebek_subpackages():
    """Packaging config should include sebek subpackages for editable installs."""
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


def test_vosk_version_synced_between_pyproject_and_requirements():
    """Speech requirements and project dependencies should use same Vosk floor."""
    root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject.get("project", {}).get("dependencies", [])
    pyproject_vosk = next(dep for dep in dependencies if dep.startswith("vosk>="))
    req_lines = (root / "requirements-speech.txt").read_text(encoding="utf-8").splitlines()
    requirements_vosk = next(line.strip() for line in req_lines if line.strip().startswith("vosk>="))
    assert pyproject_vosk == requirements_vosk

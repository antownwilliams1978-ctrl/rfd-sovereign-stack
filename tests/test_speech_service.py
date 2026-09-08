"""Tests for speech-agent process management helpers."""

import json
import signal
from unittest.mock import MagicMock, patch

from sebek.services.speech_service import (
    get_agent_status,
    get_runtime_paths,
    start_agent,
    stop_agent,
)


class TestSpeechService:
    """Test speech-agent service helpers."""

    @patch("sebek.services.speech_service.time.sleep", return_value=None)
    @patch("sebek.services.speech_service._is_agent_process", return_value=True)
    @patch("sebek.services.speech_service._pid_exists", return_value=True)
    @patch("sebek.services.speech_service.subprocess.run")
    def test_start_agent_uses_package_entrypoint(
        self,
        mock_run,
        _mock_pid_exists,
        _mock_is_agent_process,
        _mock_sleep,
        temp_dir,
    ):
        """Start should launch the package-native speech agent command."""
        mock_run.return_value = MagicMock(stdout="4242\n")

        status = start_agent(persist_dir=temp_dir)
        paths = get_runtime_paths(temp_dir)

        assert status["running"] is True
        assert status["pid"] == 4242
        command = mock_run.call_args.args[0]
        assert command[:2] == ["bash", "-lc"]
        shell_command = command[2]
        assert "sebek.speech.agent" in shell_command
        assert str(paths["status_file"]) in shell_command
        assert paths["pid_file"].read_text(encoding="utf-8").strip() == "4242"

    @patch("sebek.services.speech_service._is_agent_process", return_value=False)
    @patch("sebek.services.speech_service._pid_exists", return_value=False)
    def test_get_agent_status_marks_stale_pid_as_stopped(
        self,
        _mock_pid_exists,
        _mock_is_agent_process,
        temp_dir,
    ):
        """Status should not report stale pid files as running."""
        paths = get_runtime_paths(temp_dir)
        paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
        paths["pid_file"].write_text("9999\n", encoding="utf-8")
        paths["status_file"].write_text(
            json.dumps({"status": "running", "running": True, "pid": 9999}),
            encoding="utf-8",
        )

        status = get_agent_status(temp_dir)

        assert status["running"] is False
        assert status["pid"] is None
        assert status["status"] == "stopped"

    @patch("sebek.services.speech_service.time.sleep", return_value=None)
    @patch("sebek.services.speech_service._pid_exists", side_effect=[True, False, False])
    @patch("sebek.services.speech_service.os.kill")
    def test_stop_agent_terminates_running_process(
        self,
        mock_kill,
        _mock_pid_exists,
        _mock_sleep,
        temp_dir,
    ):
        """Stop should terminate the tracked speech agent and clear pid state."""
        paths = get_runtime_paths(temp_dir)
        paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
        paths["pid_file"].write_text("5150\n", encoding="utf-8")
        paths["status_file"].write_text(
            json.dumps({"status": "running", "running": True, "pid": 5150}),
            encoding="utf-8",
        )

        status = stop_agent(temp_dir)

        mock_kill.assert_called_once_with(5150, signal.SIGTERM)
        assert status["running"] is False
        assert status["status"] == "stopped"
        assert not paths["pid_file"].exists()

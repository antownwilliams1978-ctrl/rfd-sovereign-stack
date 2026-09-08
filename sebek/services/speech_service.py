"""Dashboard-facing helpers for managing the SEBEK speech agent."""

from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from sebek.config import Config

REPO_ROOT = Path(__file__).resolve().parents[2]
PID_FILE_NAME = "speech_agent.pid"
STATUS_FILE_NAME = "speech_agent_status.json"
LOG_FILE_NAME = "speech_agent.log"
_STATUS_KEYS = {
    "status": "stopped",
    "running": False,
    "pid": None,
    "started_at": None,
    "updated_at": None,
    "last_transcript": None,
    "last_observation_source": None,
    "last_error": None,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_runtime_paths(persist_dir: Optional[Path] = None) -> Dict[str, Path]:
    """Return speech-agent runtime file locations."""
    runtime_dir = Path(persist_dir or Config.speech.persist_dir)
    return {
        "runtime_dir": runtime_dir,
        "pid_file": runtime_dir / PID_FILE_NAME,
        "status_file": runtime_dir / STATUS_FILE_NAME,
        "log_file": runtime_dir / LOG_FILE_NAME,
    }


def _ensure_runtime_dir(persist_dir: Optional[Path] = None) -> Dict[str, Path]:
    paths = get_runtime_paths(persist_dir)
    paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
    return paths


def read_agent_status(status_file: Optional[Path] = None) -> Dict[str, Any]:
    """Read the persisted speech-agent status."""
    if status_file is None:
        status_file = get_runtime_paths()["status_file"]

    payload = dict(_STATUS_KEYS)
    if status_file.exists():
        try:
            payload.update(json.loads(status_file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            payload["status"] = "error"
            payload["last_error"] = f"Invalid status file: {status_file}"
    return payload


def write_agent_status(
    *,
    status_file: Optional[Path] = None,
    persist_dir: Optional[Path] = None,
    **updates: Any,
) -> Dict[str, Any]:
    """Persist speech-agent status for dashboard reads."""
    paths = _ensure_runtime_dir(persist_dir)
    status_file = status_file or paths["status_file"]
    payload = read_agent_status(status_file)
    payload.update(updates)
    if "running" not in updates:
        payload["running"] = payload.get("status") in {"starting", "running"}
    payload["updated_at"] = _utc_now()

    tmp_path = status_file.with_suffix(status_file.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(status_file)
    return payload


def _read_pid(pid_file: Path) -> Optional[int]:
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _write_pid(pid_file: Path, pid: int) -> None:
    pid_file.write_text(f"{pid}\n", encoding="utf-8")


def _remove_file(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _process_command(pid: int) -> str:
    proc_cmdline = Path(f"/proc/{pid}/cmdline")
    if proc_cmdline.exists():
        try:
            return proc_cmdline.read_text(encoding="utf-8", errors="ignore").replace("\x00", " ")
        except OSError:
            return ""

    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    return result.stdout.strip()


def _is_agent_process(pid: int) -> bool:
    command = _process_command(pid)
    return True if not command else "sebek.speech.agent" in command


def get_agent_status(persist_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Return computed speech-agent status using persisted disk state."""
    paths = get_runtime_paths(persist_dir)
    status = read_agent_status(paths["status_file"])
    pid = _read_pid(paths["pid_file"]) or status.get("pid")

    if pid and _pid_exists(pid) and _is_agent_process(pid):
        status["pid"] = pid
        status["running"] = True
        if status.get("status") in {"stopped", "error"}:
            status["status"] = "running"
    else:
        status["running"] = False
        status["pid"] = None
        if status.get("status") in {"starting", "running"}:
            status["status"] = "stopped" if not status.get("last_error") else "error"

    return status


def build_agent_command(
    *,
    model_path: Optional[Path] = None,
    persist_dir: Optional[Path] = None,
    sebek_url: Optional[str] = None,
    enable_tts: Optional[bool] = None,
    log_level: str = "INFO",
    status_file: Optional[Path] = None,
) -> list[str]:
    """Build the package-native speech-agent command."""
    paths = get_runtime_paths(persist_dir)
    command = [
        sys.executable,
        "-m",
        "sebek.speech.agent",
        "--model",
        str(model_path or Config.speech.vosk_model_path),
        "--persist-dir",
        str(persist_dir or Config.speech.persist_dir),
        "--sebek-url",
        sebek_url or Config.ollama.api_observe_endpoint,
        "--status-file",
        str(status_file or paths["status_file"]),
        "--log-level",
        log_level,
    ]
    if enable_tts is False:
        command.append("--no-tts")
    return command


def start_agent(
    *,
    model_path: Optional[Path] = None,
    persist_dir: Optional[Path] = None,
    sebek_url: Optional[str] = None,
    enable_tts: Optional[bool] = None,
    log_level: str = "INFO",
) -> Dict[str, Any]:
    """Start the speech agent as a detached subprocess."""
    current = get_agent_status(persist_dir)
    if current["running"]:
        return current

    paths = _ensure_runtime_dir(persist_dir)
    command = build_agent_command(
        model_path=model_path,
        persist_dir=paths["runtime_dir"],
        sebek_url=sebek_url,
        enable_tts=enable_tts,
        log_level=log_level,
        status_file=paths["status_file"],
    )
    write_agent_status(
        status_file=paths["status_file"],
        status="starting",
        running=False,
        pid=None,
        started_at=_utc_now(),
        last_error=None,
    )

    if os.name == "nt":
        popen_kwargs: Dict[str, Any] = {
            "cwd": str(REPO_ROOT),
            "stdout": open(paths["log_file"], "a", encoding="utf-8"),
            "stderr": subprocess.STDOUT,
            "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        }
        process = subprocess.Popen(command, **popen_kwargs)
        popen_kwargs["stdout"].close()
        pid = process.pid
    else:
        shell_command = (
            f"cd {shlex.quote(str(REPO_ROOT))} && "
            f"nohup {shlex.join(command)} >> {shlex.quote(str(paths['log_file']))} "
            "2>&1 < /dev/null & echo $!"
        )
        result = subprocess.run(
            ["bash", "-lc", shell_command],
            check=True,
            capture_output=True,
            text=True,
        )
        pid = int(result.stdout.strip().splitlines()[-1])

    _write_pid(paths["pid_file"], pid)
    write_agent_status(
        status_file=paths["status_file"],
        status="running",
        running=True,
        pid=pid,
    )

    time.sleep(0.2)
    current = get_agent_status(paths["runtime_dir"])
    if not current["running"] and current.get("status") != "running":
        _remove_file(paths["pid_file"])
        write_agent_status(
            status_file=paths["status_file"],
            status="error",
            running=False,
            pid=None,
            last_error=current.get("last_error") or "Speech agent exited during startup",
        )

    return get_agent_status(paths["runtime_dir"])


def stop_agent(persist_dir: Optional[Path] = None, timeout: float = 5.0) -> Dict[str, Any]:
    """Stop the running speech agent process."""
    paths = get_runtime_paths(persist_dir)
    current = get_agent_status(persist_dir)
    pid = current.get("pid")
    if not pid:
        _remove_file(paths["pid_file"])
        return current

    try:
        os.kill(pid, signal.SIGTERM)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not _pid_exists(pid):
                break
            time.sleep(0.1)
        if _pid_exists(pid) and hasattr(signal, "SIGKILL"):
            os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
    finally:
        _remove_file(paths["pid_file"])
        write_agent_status(
            status_file=paths["status_file"],
            status="stopped",
            running=False,
            pid=None,
        )

    return get_agent_status(persist_dir)

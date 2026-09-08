#!/usr/bin/env python3
"""Legacy speech-agent entrypoint.

Deprecated: use package-native launch path:
  - python -m sebek.speech.agent
"""

from warnings import warn

from sebek.speech.agent import main as speech_main


def main() -> int:
    warn(
        "sebek_speech_agent.py is deprecated; use `python -m sebek.speech.agent`.",
        DeprecationWarning,
        stacklevel=2,
    )
    return speech_main()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Legacy ingestion entrypoint.

Deprecated: use package-native launch paths:
  - python -m sebek.ingestion_cli
  - sebek-ingestion
"""

from warnings import warn

def main() -> int:
    from sebek.ingestion_cli import main as ingestion_main

    warn(
        "sebek_mass_digest.py is deprecated; use `python -m sebek.ingestion_cli` "
        "or `sebek-ingestion`.",
        DeprecationWarning,
        stacklevel=2,
    )
    return ingestion_main()


if __name__ == "__main__":
    raise SystemExit(main())

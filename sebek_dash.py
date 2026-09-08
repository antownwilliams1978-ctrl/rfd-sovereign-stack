#!/usr/bin/env python3
"""Legacy dashboard entrypoint.

Deprecated: use package-native launch paths:
  - streamlit run sebek/dashboard.py
  - python -m sebek.dashboard
"""

from warnings import warn

from sebek.dashboard import main as dashboard_main


def main() -> None:
    warn(
        "sebek_dash.py is deprecated; use `streamlit run sebek/dashboard.py` "
        "or `python -m sebek.dashboard`.",
        DeprecationWarning,
        stacklevel=2,
    )
    dashboard_main()


if __name__ == "__main__":
    main()

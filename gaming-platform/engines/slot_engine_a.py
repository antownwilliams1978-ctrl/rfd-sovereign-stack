"""Compatibility wrapper for the Slot Engine A entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from gaming_platform.audit import AuditTrail
from gaming_platform.engines.slot_engine_a import SlotEngineA
from gaming_platform.models import CoinType, SpinResult, SymbolType

__all__ = ["CoinType", "SlotEngineA", "SpinResult", "SymbolType"]


def build_parser() -> argparse.ArgumentParser:
    """Build the slot engine CLI parser."""

    parser = argparse.ArgumentParser(description="Play one or more Slot Engine A spins.")
    parser.add_argument("--coin-type", choices=[coin.value for coin in CoinType], default="GC")
    parser.add_argument("--wager", type=int, default=100)
    parser.add_argument("--spins", type=int, default=1)
    parser.add_argument("--audit-log", type=Path, default=PACKAGE_ROOT / "logs" / "slot_engine_audit.log")
    return parser


def render_spin(result: SpinResult) -> str:
    """Render a spin result for terminal output."""

    lines = [
        f"{result.spin_id}: wager={result.wager} {result.coin_type} win={result.total_win} net={result.net_result:+d}",
        "grid:",
    ]
    lines.extend(f"  {' | '.join(row)}" for row in result.symbols)
    lines.append(f"wilds={result.wild_positions} multipliers={result.wild_multipliers}")

    if result.payline_wins:
        for win in result.payline_wins:
            lines.append(
                f"win -> {win['payline']}: {win['symbol']} x{win['count']} = "
                f"{win['payout']} (base={win['base_payout']} x {win['multiplier']}x)"
            )
    else:
        lines.append("win -> no paylines hit")

    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the slot engine CLI."""

    args = build_parser().parse_args(argv)
    audit_path = args.audit_log
    engine = SlotEngineA(audit_trail=AuditTrail.from_path(audit_path))

    print("\n" + "=" * 80)
    print("SLOT ENGINE A")
    print("=" * 80)

    for spin_number in range(1, args.spins + 1):
        result = engine.spin(coin_type=args.coin_type, wager=args.wager)
        print(f"\n--- Spin {spin_number} of {args.spins} ---")
        print(render_spin(result))

    print("\n" + "=" * 80)
    print("ENGINE STATISTICS")
    print("=" * 80)
    for key, value in engine.get_statistics().items():
        print(f"{key}: {value}")

    print(f"\nAudit logs written to: {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

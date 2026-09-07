"""Compatibility wrapper for the Slot Engine A entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from gaming_platform.audit import AuditTrail
from gaming_platform.engines.slot_engine_a import SlotEngineA
from gaming_platform.models import CoinType, SpinResult, SymbolType

__all__ = ["CoinType", "SlotEngineA", "SpinResult", "SymbolType"]


def main() -> None:
    """Run a small local demo."""

    audit_path = PACKAGE_ROOT / "logs" / "slot_engine_audit.log"
    engine = SlotEngineA(audit_trail=AuditTrail.from_path(audit_path))

    print("\n" + "=" * 80)
    print("SLOT ENGINE A: FOUNDATION DEMO")
    print("=" * 80)

    for coin_type, wager, label, total_spins in (("GC", 100, "GC Spins", 5), ("SC", 50, "SC Spins", 3)):
        print(f"\n--- {label} ---")
        for _ in range(total_spins):
            result = engine.spin(coin_type=coin_type, wager=wager)
            print(
                f"\n{result.spin_id}: wager={result.wager} {result.coin_type} "
                f"win={result.total_win} net={result.net_result:+d}"
            )
            print(f"  wilds={result.wild_positions} multipliers={result.wild_multipliers}")
            for win in result.payline_wins:
                print(
                    f"  -> {win['payline']}: {win['symbol']} x{win['count']} "
                    f"= {win['payout']} (base={win['base_payout']} x {win['multiplier']}x)"
                )

    print("\n" + "=" * 80)
    print("ENGINE STATISTICS")
    print("=" * 80)
    for key, value in engine.get_statistics().items():
        print(f"{key}: {value}")

    print(f"\nAudit logs written to: {audit_path}")


if __name__ == "__main__":
    main()

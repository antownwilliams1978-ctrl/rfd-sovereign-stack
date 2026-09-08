"""Ledger service scaffolding for wagering and payouts."""

from __future__ import annotations

from dataclasses import dataclass, field

from gaming_platform.models import SpinResult


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """Immutable accounting entry."""

    spin_id: str
    coin_type: str
    amount: int
    entry_type: str


@dataclass(slots=True)
class InMemoryLedgerService:
    """In-memory ledger boundary for early platform development."""

    entries: list[LedgerEntry] = field(default_factory=list)

    def record_spin(self, result: SpinResult) -> None:
        """Record wager and payout entries for a spin."""

        self.entries.append(
            LedgerEntry(
                spin_id=result.spin_id,
                coin_type=result.coin_type,
                amount=-result.wager,
                entry_type="wager",
            )
        )

        if result.total_win > 0:
            self.entries.append(
                LedgerEntry(
                    spin_id=result.spin_id,
                    coin_type=result.coin_type,
                    amount=result.total_win,
                    entry_type="payout",
                )
            )

"""Shared gaming platform models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class SymbolType(str, Enum):
    """Supported slot symbols."""

    FEATHER = "feather"
    BUFFALO = "buffalo"
    COUNCIL = "council"
    RIVER = "river"
    DRUM = "drum"
    FIRE = "fire"
    WILD = "wild"


class CoinType(str, Enum):
    """Supported wagering currencies."""

    GC = "GC"
    SC = "SC"


class PaylineWinData(TypedDict):
    """Serialized payline win structure."""

    payline: str
    symbol: str
    count: int
    base_payout: int
    multiplier: int
    payout: int


@dataclass(frozen=True, slots=True)
class SpinResult:
    """Complete spin outcome."""

    spin_id: str
    timestamp: str
    coin_type: str
    wager: int
    symbols: list[list[str]]
    payline_wins: list[PaylineWinData]
    wild_positions: list[tuple[int, int]]
    wild_multipliers: list[int]
    total_win: int
    net_result: int
    rng_seed: str
    house_edge_applied: bool

    def to_audit_payload(self) -> dict[str, object]:
        """Return a structured audit payload."""

        return {
            "event": "spin.completed",
            "spin_id": self.spin_id,
            "timestamp": self.timestamp,
            "coin_type": self.coin_type,
            "wager": self.wager,
            "symbols": self.symbols,
            "payline_wins": self.payline_wins,
            "wild_positions": self.wild_positions,
            "wild_multipliers": self.wild_multipliers,
            "total_win": self.total_win,
            "net_result": self.net_result,
            "rng_seed": self.rng_seed,
            "house_edge_applied": self.house_edge_applied,
        }

"""Typed configuration for gaming platform engines."""

from __future__ import annotations

from dataclasses import dataclass, field

from gaming_platform.models import CoinType, SymbolType


@dataclass(frozen=True, slots=True)
class SlotEngineConfig:
    """Configuration for slot engine behavior."""

    symbol_weights: dict[SymbolType, int]
    paylines: dict[str, tuple[tuple[int, int], ...]]
    payout_table: dict[SymbolType, dict[int, int]]
    house_edge: dict[CoinType, float]
    reels: int = 5
    rows: int = 3
    wild_count_range: tuple[int, int] = (1, 3)
    wild_multiplier_weights: dict[int, int] = field(
        default_factory=lambda: {1: 40, 2: 30, 3: 15, 4: 10, 5: 5}
    )

    def __post_init__(self) -> None:
        """Validate configuration invariants."""

        if self.reels <= 0 or self.rows <= 0:
            raise ValueError("reels and rows must be positive")
        if len(self.symbol_weights) == 0:
            raise ValueError("symbol_weights must not be empty")
        if self.wild_count_range[0] <= 0 or self.wild_count_range[0] > self.wild_count_range[1]:
            raise ValueError("wild_count_range must define a valid positive range")
        if any(weight <= 0 for weight in self.symbol_weights.values()):
            raise ValueError("symbol weights must be positive")
        if any(weight <= 0 for weight in self.wild_multiplier_weights.values()):
            raise ValueError("wild multiplier weights must be positive")


DEFAULT_SLOT_ENGINE_CONFIG = SlotEngineConfig(
    symbol_weights={
        SymbolType.FEATHER: 25,
        SymbolType.BUFFALO: 25,
        SymbolType.COUNCIL: 20,
        SymbolType.RIVER: 15,
        SymbolType.DRUM: 10,
        SymbolType.FIRE: 5,
    },
    paylines={
        "center": ((0, 1), (1, 1), (2, 1), (3, 1), (4, 1)),
        "top": ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0)),
        "bottom": ((0, 2), (1, 2), (2, 2), (3, 2), (4, 2)),
    },
    payout_table={
        SymbolType.FEATHER: {3: 10, 4: 50, 5: 500},
        SymbolType.BUFFALO: {3: 15, 4: 75, 5: 750},
        SymbolType.COUNCIL: {3: 20, 4: 100, 5: 1000},
        SymbolType.RIVER: {3: 25, 4: 125, 5: 1250},
        SymbolType.DRUM: {3: 30, 4: 150, 5: 1500},
        SymbolType.FIRE: {3: 50, 4: 250, 5: 2500},
    },
    house_edge={
        CoinType.GC: 0.08,
        CoinType.SC: 0.06,
    },
)

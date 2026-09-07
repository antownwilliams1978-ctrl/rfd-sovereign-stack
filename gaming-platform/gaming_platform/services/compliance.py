"""Compliance guardrails for platform services."""

from __future__ import annotations

from dataclasses import dataclass, field

from gaming_platform.models import CoinType


class ComplianceError(ValueError):
    """Raised when a request fails compliance validation."""


@dataclass(frozen=True, slots=True)
class CompliancePolicy:
    """Minimal spin validation policy."""

    min_wager: int = 1
    max_wager: int = 100_000
    allowed_coin_types: frozenset[CoinType] = field(default_factory=lambda: frozenset(CoinType))

    def validate_spin(self, coin_type: str, wager: int) -> CoinType:
        """Validate a spin request and normalize its coin type."""

        try:
            normalized_coin_type = CoinType(coin_type)
        except ValueError as exc:
            raise ComplianceError(f"Unsupported coin type: {coin_type}") from exc

        if normalized_coin_type not in self.allowed_coin_types:
            raise ComplianceError(f"Coin type is not enabled: {coin_type}")
        if wager < self.min_wager:
            raise ComplianceError("Wager must be positive")
        if wager > self.max_wager:
            raise ComplianceError("Wager exceeds configured maximum")

        return normalized_coin_type

"""Typed slot engine foundation for the gaming platform."""

from __future__ import annotations

import json
import random
import secrets
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Callable

from gaming_platform.audit import AuditTrail, build_logger
from gaming_platform.config import DEFAULT_SLOT_ENGINE_CONFIG, SlotEngineConfig
from gaming_platform.models import CoinType, PaylineWinData, SpinResult, SymbolType
from gaming_platform.services import (
    AdminService,
    CompliancePolicy,
    InMemoryLedgerService,
    InMemoryTelemetryService,
)


class SlotEngineA:
    """5x3 slot engine with configurable paylines, audit, and service boundaries."""

    def __init__(
        self,
        *,
        config: SlotEngineConfig | None = None,
        audit_trail: AuditTrail | None = None,
        ledger_service: InMemoryLedgerService | None = None,
        compliance_policy: CompliancePolicy | None = None,
        telemetry_service: InMemoryTelemetryService | None = None,
        admin_service: AdminService | None = None,
        seed_provider: Callable[[], str] | None = None,
    ) -> None:
        self.config = config or DEFAULT_SLOT_ENGINE_CONFIG
        self.audit_trail = audit_trail or AuditTrail.from_path()
        self.ledger_service = ledger_service or InMemoryLedgerService()
        self.compliance_policy = compliance_policy or CompliancePolicy()
        self.telemetry_service = telemetry_service or InMemoryTelemetryService()
        self.admin_service = admin_service or AdminService()
        self.seed_provider = seed_provider or (lambda: secrets.token_hex(16))
        self.logger = build_logger("gaming_platform.engine")

        self.spin_counter = 0
        self.total_wagered = 0
        self.total_paid = 0

        self.logger.info(
            json.dumps(
                {
                    "event": "engine.initialized",
                    "engine": "SlotEngineA",
                    "reels": self.config.reels,
                    "rows": self.config.rows,
                    "paylines": list(self.config.paylines.keys()),
                },
                sort_keys=True,
            )
        )

    def spin(self, coin_type: str = "GC", wager: int = 100) -> SpinResult:
        """Execute a single spin."""

        normalized_coin_type = self.compliance_policy.validate_spin(coin_type, wager)
        self.spin_counter += 1
        self.total_wagered += wager

        rng_seed = self.seed_provider()
        rng = random.Random(rng_seed)
        spin_id = f"SPIN_{self.spin_counter:06d}"

        symbols = self._generate_symbols(rng)
        symbols, wild_positions, wild_multipliers = self._apply_wilds(symbols, rng)
        payline_wins = self._evaluate_paylines(symbols, wild_positions, wild_multipliers)

        total_win = sum(win["payout"] for win in payline_wins)
        total_win, house_edge_applied = self._apply_house_edge(
            wager=wager,
            total_win=total_win,
            house_edge_target=self.config.house_edge[normalized_coin_type],
        )
        self.total_paid += total_win

        result = SpinResult(
            spin_id=spin_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            coin_type=normalized_coin_type.value,
            wager=wager,
            symbols=self._serialize_symbols(symbols),
            payline_wins=payline_wins,
            wild_positions=wild_positions,
            wild_multipliers=wild_multipliers,
            total_win=total_win,
            net_result=total_win - wager,
            rng_seed=rng_seed,
            house_edge_applied=house_edge_applied,
        )

        self.ledger_service.record_spin(result)
        self.telemetry_service.record_spin(result)
        self.audit_trail.record_spin(result)

        return result

    def _generate_symbols(self, rng: random.Random) -> list[list[SymbolType]]:
        """Generate a 5x3 symbol grid."""

        symbols: list[list[SymbolType]] = []
        weighted_symbols = list(self.config.symbol_weights.keys())
        weights = list(self.config.symbol_weights.values())

        for _ in range(self.config.reels):
            reel_symbols: list[SymbolType] = []
            for _ in range(self.config.rows):
                reel_symbols.append(rng.choices(weighted_symbols, weights=weights, k=1)[0])
            symbols.append(reel_symbols)

        return symbols

    def _apply_wilds(
        self,
        symbols: list[list[SymbolType]],
        rng: random.Random,
    ) -> tuple[list[list[SymbolType]], list[tuple[int, int]], list[int]]:
        """Apply a small number of wild symbols."""

        wild_positions: list[tuple[int, int]] = []
        wild_multipliers: list[int] = []
        num_wilds = rng.randint(*self.config.wild_count_range)

        weighted_multipliers = list(self.config.wild_multiplier_weights.keys())
        weights = list(self.config.wild_multiplier_weights.values())

        while len(wild_positions) < num_wilds:
            position = (rng.randint(0, self.config.reels - 1), rng.randint(0, self.config.rows - 1))
            if position in wild_positions:
                continue

            reel, row = position
            symbols[reel][row] = SymbolType.WILD
            wild_positions.append(position)
            wild_multipliers.append(rng.choices(weighted_multipliers, weights=weights, k=1)[0])

        return symbols, wild_positions, wild_multipliers

    def _evaluate_paylines(
        self,
        symbols: list[list[SymbolType]],
        wild_positions: list[tuple[int, int]],
        wild_multipliers: list[int],
    ) -> list[PaylineWinData]:
        """Evaluate configured paylines."""

        wins: list[PaylineWinData] = []
        wild_dict = {position: multiplier for position, multiplier in zip(wild_positions, wild_multipliers)}

        for payline_name, payline in self.config.paylines.items():
            payline_symbols = [symbols[reel][row] for reel, row in payline]
            match = self._check_match(payline_symbols)
            if match is None:
                continue

            symbol_type, count = match
            base_payout = self.config.payout_table[symbol_type].get(count, 0)
            if base_payout == 0:
                continue

            multiplier = self._calculate_multiplier(payline, wild_dict)
            wins.append(
                {
                    "payline": payline_name,
                    "symbol": symbol_type.value,
                    "count": count,
                    "base_payout": base_payout,
                    "multiplier": multiplier,
                    "payout": base_payout * multiplier,
                }
            )

        return wins

    def _check_match(self, payline_symbols: list[SymbolType]) -> tuple[SymbolType, int] | None:
        """Return the left-to-right matching symbol and count."""

        anchor = next((symbol for symbol in payline_symbols if symbol is not SymbolType.WILD), None)
        if anchor is None:
            return None

        count = 0
        for symbol in payline_symbols:
            if symbol in (anchor, SymbolType.WILD):
                count += 1
                continue
            break

        if count >= 3:
            return anchor, count

        return None

    def _calculate_multiplier(
        self,
        payline: tuple[tuple[int, int], ...],
        wild_dict: dict[tuple[int, int], int],
    ) -> int:
        """Calculate the bounded multiplier for a payline."""

        multiplier = 1
        for position in payline:
            multiplier *= wild_dict.get(position, 1)
        return min(multiplier, max(self.config.wild_multiplier_weights))

    def _apply_house_edge(
        self,
        *,
        wager: int,
        total_win: int,
        house_edge_target: float,
    ) -> tuple[int, bool]:
        """Apply a simple sustainability cap when needed."""

        accumulated_edge = (
            (self.total_wagered - self.total_paid) / self.total_wagered
            if self.total_wagered > 0
            else house_edge_target
        )
        if accumulated_edge < house_edge_target:
            max_win = int(wager * (1 - house_edge_target))
            adjusted_win = min(total_win, max_win)
            if adjusted_win < total_win:
                self.logger.info(
                    json.dumps(
                        {
                            "event": "house_edge.applied",
                            "requested_win": total_win,
                            "adjusted_win": adjusted_win,
                            "accumulated_edge": round(accumulated_edge, 6),
                            "target_edge": house_edge_target,
                        },
                        sort_keys=True,
                    )
                )
                return adjusted_win, True
        return total_win, False

    def _serialize_symbols(self, symbols: list[list[SymbolType]]) -> list[list[str]]:
        """Convert reel-major symbols into row-major strings."""

        return [
            [symbols[reel][row].value for reel in range(self.config.reels)]
            for row in range(self.config.rows)
        ]

    def get_statistics(self) -> dict[str, object]:
        """Return engine statistics for monitoring."""

        if self.total_wagered == 0:
            return {"status": "no_spins_yet"}

        rtp = (self.total_paid / self.total_wagered) * 100
        snapshot = self.admin_service.build_snapshot(
            total_spins=self.spin_counter,
            total_wagered=self.total_wagered,
            total_paid=self.total_paid,
            ledger=self.ledger_service,
            telemetry=self.telemetry_service,
        )
        payload = asdict(snapshot)
        payload.update(
            {
                "RTP": f"{rtp:.2f}%",
                "house_edge": f"{100 - rtp:.2f}%",
                "target_edge_GC": "8.00%",
                "target_edge_SC": "6.00%",
            }
        )
        return payload

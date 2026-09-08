"""Tests for the gaming platform foundation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
GAMING_PLATFORM_ROOT = ROOT / "gaming-platform"
if str(GAMING_PLATFORM_ROOT) not in sys.path:
    sys.path.insert(0, str(GAMING_PLATFORM_ROOT))

from engines import slot_engine_a as slot_engine_cli
from gaming_platform.audit import AuditTrail
from gaming_platform.engines.slot_engine_a import SlotEngineA
from gaming_platform.models import SpinResult, SymbolType


class TestSlotEngineA:
    """Test the slot engine foundation behavior."""

    def test_engine_initialization_has_safe_defaults(self, tmp_path):
        """Test initialization does not require eager filesystem setup."""

        engine = SlotEngineA(audit_trail=AuditTrail.from_path(tmp_path / "audit.log"))

        assert engine.spin_counter == 0
        assert engine.total_wagered == 0
        assert engine.total_paid == 0
        assert engine.get_statistics() == {"status": "no_spins_yet"}
        assert engine.ledger_service.entries == []
        assert engine.telemetry_service.events == []

    def test_spin_records_audit_and_service_events(self, tmp_path):
        """Test a spin updates audit, ledger, and telemetry services."""

        audit_path = tmp_path / "audit.log"
        engine = SlotEngineA(
            audit_trail=AuditTrail.from_path(audit_path),
            seed_provider=iter(["unit-test-seed"]).__next__,
        )

        result = engine.spin(coin_type="GC", wager=100)

        assert result.spin_id == "SPIN_000001"
        assert result.coin_type == "GC"
        assert result.wager == 100
        assert len(result.symbols) == 3
        assert all(len(row) == 5 for row in result.symbols)
        assert engine.spin_counter == 1
        assert engine.total_wagered == 100
        assert len(engine.ledger_service.entries) >= 1
        assert engine.telemetry_service.summary()["spins"] == 1

        audit_payload = json.loads(audit_path.read_text().strip().splitlines()[-1])
        assert audit_payload["event"] == "spin.completed"
        assert audit_payload["spin_id"] == result.spin_id
        assert audit_payload["coin_type"] == result.coin_type

    def test_payline_evaluation_applies_wild_substitution_and_multiplier(self):
        """Test wild symbols substitute and multiply configured paylines."""

        engine = SlotEngineA()
        symbols = [
            [SymbolType.BUFFALO, SymbolType.FIRE, SymbolType.DRUM],
            [SymbolType.COUNCIL, SymbolType.FIRE, SymbolType.RIVER],
            [SymbolType.DRUM, SymbolType.WILD, SymbolType.BUFFALO],
            [SymbolType.RIVER, SymbolType.FIRE, SymbolType.COUNCIL],
            [SymbolType.DRUM, SymbolType.FIRE, SymbolType.BUFFALO],
        ]

        wins = engine._evaluate_paylines(symbols, [(2, 1)], [3])

        assert wins == [
            {
                "payline": "center",
                "symbol": "fire",
                "count": 5,
                "base_payout": 2500,
                "multiplier": 3,
                "payout": 7500,
            }
        ]


class TestSlotEngineCLI:
    """Test the CLI wrapper for manual spins."""

    def test_render_spin_includes_grid_and_win_details(self):
        """Test rendered spin output is human-friendly."""

        rendered = slot_engine_cli.render_spin(
            SpinResult(
                spin_id="SPIN_000001",
                timestamp="2026-01-01T00:00:00+00:00",
                coin_type="GC",
                wager=100,
                symbols=[
                    ["feather", "buffalo", "wild", "river", "drum"],
                    ["fire", "fire", "fire", "council", "river"],
                    ["drum", "river", "buffalo", "buffalo", "buffalo"],
                ],
                payline_wins=[
                    {
                        "payline": "center",
                        "symbol": "fire",
                        "count": 3,
                        "base_payout": 50,
                        "multiplier": 2,
                        "payout": 100,
                    }
                ],
                wild_positions=[(2, 0)],
                wild_multipliers=[2],
                total_win=100,
                net_result=0,
                rng_seed="seed",
                house_edge_applied=False,
            )
        )

        assert "SPIN_000001" in rendered
        assert "grid:" in rendered
        assert "feather | buffalo | wild | river | drum" in rendered
        assert "win -> center: fire x3 = 100" in rendered

    def test_main_runs_single_spin_from_cli_args(self, tmp_path, capsys):
        """Test CLI plays one spin with provided arguments."""

        audit_path = tmp_path / "slot_audit.log"
        with patch.object(sys, "argv", ["slot_engine_a.py", "--coin-type", "SC", "--wager", "50", "--audit-log", str(audit_path)]):
            exit_code = slot_engine_cli.main()

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Spin 1 of 1" in captured.out
        assert "SC" in captured.out
        assert audit_path.exists()

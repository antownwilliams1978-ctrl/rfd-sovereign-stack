"""Admin and backoffice scaffolding."""

from __future__ import annotations

from dataclasses import dataclass

from gaming_platform.services.ledger import InMemoryLedgerService
from gaming_platform.services.telemetry import InMemoryTelemetryService


@dataclass(frozen=True, slots=True)
class PlatformSnapshot:
    """Minimal backoffice view of engine health."""

    total_spins: int
    total_wagered: int
    total_paid: int
    ledger_entries: int
    telemetry_events: int


class AdminService:
    """Read-only operational summary service."""

    def build_snapshot(
        self,
        *,
        total_spins: int,
        total_wagered: int,
        total_paid: int,
        ledger: InMemoryLedgerService,
        telemetry: InMemoryTelemetryService,
    ) -> PlatformSnapshot:
        """Create a summary suitable for backoffice views."""

        return PlatformSnapshot(
            total_spins=total_spins,
            total_wagered=total_wagered,
            total_paid=total_paid,
            ledger_entries=len(ledger.entries),
            telemetry_events=len(telemetry.events),
        )

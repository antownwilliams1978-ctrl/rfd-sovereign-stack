"""Telemetry service scaffolding."""

from __future__ import annotations

from dataclasses import dataclass, field

from gaming_platform.models import SpinResult


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    """Simple telemetry event."""

    event_type: str
    spin_id: str
    total_win: int
    house_edge_applied: bool


@dataclass(slots=True)
class InMemoryTelemetryService:
    """Minimal telemetry collector for engine events."""

    events: list[TelemetryEvent] = field(default_factory=list)

    def record_spin(self, result: SpinResult) -> None:
        """Store a telemetry event for a completed spin."""

        self.events.append(
            TelemetryEvent(
                event_type="spin.completed",
                spin_id=result.spin_id,
                total_win=result.total_win,
                house_edge_applied=result.house_edge_applied,
            )
        )

    def summary(self) -> dict[str, int]:
        """Return a minimal operational summary."""

        return {
            "spins": len(self.events),
            "winning_spins": sum(1 for event in self.events if event.total_win > 0),
        }

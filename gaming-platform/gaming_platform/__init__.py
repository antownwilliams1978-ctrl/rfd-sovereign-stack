"""Gaming platform foundation package."""

from gaming_platform.config import DEFAULT_SLOT_ENGINE_CONFIG, SlotEngineConfig
from gaming_platform.models import CoinType, PaylineWinData, SpinResult, SymbolType
from gaming_platform.engines.slot_engine_a import SlotEngineA

__all__ = [
    "CoinType",
    "DEFAULT_SLOT_ENGINE_CONFIG",
    "PaylineWinData",
    "SlotEngineA",
    "SlotEngineConfig",
    "SpinResult",
    "SymbolType",
]

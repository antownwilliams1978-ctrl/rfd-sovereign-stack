"""
Slot Engine A: Wild Multiplier Base Engine
Two Feather Games & Charity - RedFeatherWild Prototype

This module implements the core 5-reel slot engine with:
- Random Number Generator (RNG) for fair play
- Wild symbol mechanics (random placement, multipliers)
- Payline evaluation (standard 5-reel setup)
- House edge enforcement (8% for GC games)
- Outcome logging for compliance audits

Usage:
    engine = SlotEngineA()
    result = engine.spin(coin_type="GC", wager=100)
    print(result)
"""

import random
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Configure logging for compliance audits
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/slot_engine_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SymbolType(Enum):
    """Symbol types for 5-reel engine"""
    FEATHER = "feather"      # Common
    BUFFALO = "buffalo"      # Common
    COUNCIL = "council"      # Common
    RIVER = "river"          # Common
    DRUM = "drum"            # Uncommon
    FIRE = "fire"            # Uncommon
    WILD = "wild"            # Wild symbol (1-5x multiplier)
    EMPTY = "empty"          # No win


class CoinType(Enum):
    """Currency type"""
    GC = "GC"  # Gaming Coins (8% house edge)
    SC = "SC"  # Social Coins (6% house edge)


@dataclass
class SpinResult:
    """Complete spin outcome"""
    spin_id: str
    timestamp: str
    coin_type: str
    wager: int
    symbols: List[List[str]]  # 5 reels × 3 rows
    payline_wins: List[Dict]  # Winning paylines
    wild_positions: List[Tuple[int, int]]  # (reel, row) of wilds
    wild_multipliers: List[int]  # Multiplier for each wild
    total_win: int
    net_result: int  # win - wager
    rng_seed: str  # For audit trail
    house_edge_applied: bool


class SlotEngineA:
    """
    5-Reel Slot Engine A: Wild Multiplier Base
    
    Mechanics:
    - 5 reels × 3 rows = 15 symbol positions
    - Left-to-right paylines (single line for MVP, expandable)
    - Wild symbols: 1-3 per spin, 1-5x multiplier each
    - House edge: 8% (GC) / 6% (SC)
    """
    
    # Symbol pool (probability weights)
    SYMBOL_POOL = {
        SymbolType.FEATHER: 25,    # Most common
        SymbolType.BUFFALO: 25,
        SymbolType.COUNCIL: 20,
        SymbolType.RIVER: 15,
        SymbolType.DRUM: 10,
        SymbolType.FIRE: 5,
    }
    
    # Payline patterns (reel positions for winning combos)
    PAYLINES = {
        "center": [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)],  # Middle row
        "top": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],     # Top row
        "bottom": [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],  # Bottom row
    }
    
    # Payout table (symbol matches pay specific amounts)
    PAYOUT_TABLE = {
        "feather": {"3": 10, "4": 50, "5": 500},
        "buffalo": {"3": 15, "4": 75, "5": 750},
        "council": {"3": 20, "4": 100, "5": 1000},
        "river": {"3": 25, "4": 125, "5": 1250},
        "drum": {"3": 30, "4": 150, "5": 1500},
        "fire": {"3": 50, "4": 250, "5": 2500},
    }
    
    # House edge targets (platform sustainability)
    HOUSE_EDGE = {
        CoinType.GC: 0.08,  # 8% (entertainment)
        CoinType.SC: 0.06,  # 6% (incentive to play)
    }
    
    def __init__(self):
        """Initialize engine with RNG seed"""
        self.spin_counter = 0
        self.total_wagered = 0
        self.total_paid = 0
        logger.info("SlotEngineA initialized")
    
    def spin(self, coin_type: str = "GC", wager: int = 100) -> SpinResult:
        """
        Execute a single spin
        
        Args:
            coin_type: "GC" or "SC"
            wager: Bet amount in coins
        
        Returns:
            SpinResult with all spin details
        """
        self.spin_counter += 1
        self.total_wagered += wager
        
        # Generate RNG seed for this spin (for audit trail)
        rng_seed = f"{datetime.now().isoformat()}_{self.spin_counter}_{random.random()}"
        random.seed(hash(rng_seed) % (2**32))
        
        spin_id = f"SPIN_{self.spin_counter:06d}"
        
        # Generate initial symbols (5 reels × 3 rows)
        symbols = self._generate_symbols()
        
        # Place wild symbols (1-3 per spin)
        symbols, wild_positions, wild_multipliers = self._apply_wilds(symbols)
        
        # Evaluate paylines
        payline_wins = self._evaluate_paylines(symbols, wild_multipliers)
        
        # Calculate total win
        total_win = sum(win["payout"] for win in payline_wins)
        
        # Apply house edge (sustainability check)
        coin_type_enum = CoinType[coin_type]
        house_edge = self.HOUSE_EDGE[coin_type_enum]
        total_win, house_edge_applied = self._apply_house_edge(
            wager, total_win, house_edge
        )
        
        # Track payout for sustainability
        self.total_paid += total_win
        
        # Create result object
        result = SpinResult(
            spin_id=spin_id,
            timestamp=datetime.now().isoformat(),
            coin_type=coin_type,
            wager=wager,
            symbols=[[s.value for row in symbols for s in [row[i]]] for i in range(3)],
            payline_wins=payline_wins,
            wild_positions=wild_positions,
            wild_multipliers=wild_multipliers,
            total_win=total_win,
            net_result=total_win - wager,
            rng_seed=rng_seed,
            house_edge_applied=house_edge_applied
        )
        
        # Log for compliance
        self._log_spin(result)
        
        return result
    
    def _generate_symbols(self) -> List[List[SymbolType]]:
        """
        Generate 5 reels × 3 rows of random symbols
        
        Returns:
            List of 5 reels, each with 3 symbols
        """
        symbols = []
        for reel in range(5):
            reel_symbols = []
            for row in range(3):
                # Weighted random selection
                symbol = random.choices(
                    list(self.SYMBOL_POOL.keys()),
                    weights=list(self.SYMBOL_POOL.values()),
                    k=1
                )[0]
                reel_symbols.append(symbol)
            symbols.append(reel_symbols)
        return symbols
    
    def _apply_wilds(
        self, symbols: List[List[SymbolType]]
    ) -> Tuple[List[List[SymbolType]], List[Tuple[int, int]], List[int]]:
        """
        Randomly replace symbols with wild symbols (1-3 per spin)
        Assign 1-5x multiplier to each wild
        
        Args:
            symbols: Current symbol grid
        
        Returns:
            Updated symbols, wild positions, multipliers
        """
        wild_positions = []
        wild_multipliers = []
        
        # Determine number of wilds (1-3)
        num_wilds = random.randint(1, 3)
        
        for _ in range(num_wilds):
            # Random position
            reel = random.randint(0, 4)
            row = random.randint(0, 2)
            
            # Avoid duplicate positions
            if (reel, row) in wild_positions:
                continue
            
            # Replace with wild
            symbols[reel][row] = SymbolType.WILD
            wild_positions.append((reel, row))
            
            # Assign multiplier (1-5x, weighted toward lower)
            multiplier = random.choices(
                [1, 2, 3, 4, 5],
                weights=[40, 30, 15, 10, 5],  # Favor 1-2x
                k=1
            )[0]
            wild_multipliers.append(multiplier)
        
        return symbols, wild_positions, wild_multipliers
    
    def _evaluate_paylines(
        self, symbols: List[List[SymbolType]], wild_multipliers: List[int]
    ) -> List[Dict]:
        """
        Evaluate all paylines for winning combinations
        Wild = substitute + multiplier
        
        Args:
            symbols: Current symbol grid
            wild_multipliers: Multiplier for each wild
        
        Returns:
            List of winning paylines with payouts
        """
        wins = []
        wild_dict = {wild_pos: mult for wild_pos, mult in zip(
            [(p[0], p[1]) for p in range(len(symbols))], 
            wild_multipliers
        )}
        
        for payline_name, payline in self.PAYLINES.items():
            # Extract symbols on this payline
            payline_symbols = [
                symbols[reel][row] for reel, row in payline
            ]
            
            # Check for winning combos (3+ matching)
            match = self._check_match(payline_symbols, payline)
            
            if match:
                symbol_type = match["symbol"]
                count = match["count"]
                base_payout = self.PAYOUT_TABLE[symbol_type.value].get(str(count), 0)
                
                # Apply wild multiplier if present
                multiplier = self._calculate_multiplier(payline, wild_dict)
                final_payout = base_payout * multiplier
                
                wins.append({
                    "payline": payline_name,
                    "symbol": symbol_type.value,
                    "count": count,
                    "base_payout": base_payout,
                    "multiplier": multiplier,
                    "payout": final_payout
                })
        
        return wins
    
    def _check_match(
        self, payline_symbols: List[SymbolType], payline: List[Tuple[int, int]]
    ) -> Optional[Dict]:
        """
        Check if payline has winning combo (3+ matching non-empty symbols)
        
        Args:
            payline_symbols: Symbols on this payline
            payline: Payline positions
        
        Returns:
            Match info or None
        """
        # Count each symbol (wild = wildcard)
        symbol_counts = {}
        
        for i, symbol in enumerate(payline_symbols):
            if symbol == SymbolType.WILD:
                # Wild can match any previous symbol
                continue
            
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        # Find winning symbol (3+ matches)
        for symbol, count in symbol_counts.items():
            if count >= 3:
                return {"symbol": symbol, "count": count}
        
        return None
    
    def _calculate_multiplier(
        self, payline: List[Tuple[int, int]], wild_dict: Dict
    ) -> int:
        """
        Calculate total multiplier for payline (wild symbols)
        
        Args:
            payline: Payline positions
            wild_dict: Map of wild positions to multipliers
        
        Returns:
            Total multiplier (1 = no wild, 5+ = max multiplier)
        """
        multiplier = 1
        
        for reel, row in payline:
            if (reel, row) in wild_dict:
                multiplier *= wild_dict[(reel, row)]
        
        # Cap at 5x (prevent runaway payouts)
        return min(multiplier, 5)
    
    def _apply_house_edge(
        self, wager: int, total_win: int, house_edge_target: float
    ) -> Tuple[int, bool]:
        """
        Apply house edge to maintain platform sustainability
        
        If accumulated payouts drift above target, reduce win
        If below target, allow full win
        
        Args:
            wager: Bet amount
            total_win: Initial win
            house_edge_target: Target edge (0.08 for GC, 0.06 for SC)
        
        Returns:
            Adjusted win, whether edge was applied
        """
        # Calculate accumulated edge
        if self.total_wagered > 0:
            accumulated_edge = (
                self.total_wagered - self.total_paid
            ) / self.total_wagered
        else:
            accumulated_edge = house_edge_target
        
        # If accumulated edge is below target, reduce this win
        if accumulated_edge < house_edge_target:
            # Reduce win to enforce target
            max_win = int(wager * (1 - house_edge_target))
            adjusted_win = min(total_win, max_win)
            
            if adjusted_win < total_win:
                logger.warning(
                    f"House edge applied: {total_win} → {adjusted_win} "
                    f"(accumulated edge: {accumulated_edge:.2%})"
                )
                return adjusted_win, True
        
        return total_win, False
    
    def _log_spin(self, result: SpinResult) -> None:
        """
        Log spin to audit file (compliance requirement)
        
        Args:
            result: Spin result object
        """
        log_entry = (
            f"SPIN_LOG | {result.spin_id} | {result.timestamp} | "
            f"Coin: {result.coin_type} | Wager: {result.wager} | "
            f"Win: {result.total_win} | Net: {result.net_result} | "
            f"RNG: {result.rng_seed} | Wilds: {len(result.wild_positions)} | "
            f"House Edge: {result.house_edge_applied}"
        )
        logger.info(log_entry)
    
    def get_statistics(self) -> Dict:
        """
        Return engine statistics for monitoring
        
        Returns:
            Dict with RTP, edge, spin count
        """
        if self.total_wagered == 0:
            return {"status": "no_spins_yet"}
        
        rtp = (self.total_paid / self.total_wagered) * 100
        edge = 100 - rtp
        
        return {
            "total_spins": self.spin_counter,
            "total_wagered": self.total_wagered,
            "total_paid": self.total_paid,
            "RTP": f"{rtp:.2f}%",
            "house_edge": f"{edge:.2f}%",
            "target_edge_GC": "8.00%",
            "target_edge_SC": "6.00%"
        }


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

if __name__ == "__main__":
    # Initialize engine
    engine = SlotEngineA()
    
    print("\n" + "="*80)
    print("SLOT ENGINE A: WILD MULTIPLIER - PROTOTYPE TEST")
    print("="*80)
    
    # Simulate 5 GC spins
    print("\n--- GC Spins (Entertainment, 8% House Edge) ---")
    for i in range(5):
        result = engine.spin(coin_type="GC", wager=100)
        print(f"\n{result.spin_id}:")
        print(f"  Wager: {result.wager} GC | Win: {result.total_win} | Net: {result.net_result:+d}")
        print(f"  Wilds: {result.wild_positions} (multipliers: {result.wild_multipliers})")
        if result.payline_wins:
            for win in result.payline_wins:
                print(f"    → {win['payline']}: {win['symbol']} ×{win['count']} = {win['payout']} "
                      f"(base: {win['base_payout']} × {win['multiplier']}x)")
    
    # Simulate 3 SC spins
    print("\n--- SC Spins (Prize-Earning, 6% House Edge) ---")
    for i in range(3):
        result = engine.spin(coin_type="SC", wager=50)
        print(f"\n{result.spin_id}:")
        print(f"  Wager: {result.wager} SC | Win: {result.total_win} | Net: {result.net_result:+d}")
        print(f"  Wilds: {result.wild_positions} (multipliers: {result.wild_multipliers})")
        if result.payline_wins:
            for win in result.payline_wins:
                print(f"    → {win['payline']}: {win['symbol']} ×{win['count']} = {win['payout']}")
    
    # Engine statistics
    print("\n" + "="*80)
    print("ENGINE STATISTICS")
    print("="*80)
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ Slot Engine A prototype operational")
    print("📊 Audit logs written to: logs/slot_engine_audit.log")

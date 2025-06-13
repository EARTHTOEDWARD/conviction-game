#!/usr/bin/env python3
"""
Conviction: A Diplomacy-style game with AI integration mechanics
Version 2.0: Three-Bloc Geopolitics

A strategy game exploring the challenges of AI adoption in the 21st century.
Players balance territorial control, technological advancement, and diplomatic
relationships while managing the friction that comes with rapid change.

Copyright (c) 2024 Conviction Game Contributors
Licensed under the MIT License
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
from collections import defaultdict

# Import the new Bloc class
from models import Bloc


@dataclass
class Unit:
    unit_id: str
    type: str
    owner: str
    location: str

    def __repr__(self):
        return f"{self.owner[0]}{self.type[0]}"

    def to_dict(self):
        return {
            "id": self.unit_id,
            "type": self.type,
            "owner": self.owner,
            "location": self.location,
        }


@dataclass
class Province:
    name: str
    adjacent_provinces: List[str] = field(default_factory=list)
    is_supply_center: bool = False
    controller: Optional[str] = None
    x: int = 0
    y: int = 0

    def to_dict(self):
        return {
            "name": self.name,
            "adjacent_to": self.adjacent_provinces,
            "is_supply_center": self.is_supply_center,
            "controller": self.controller,
        }


# Remove the old Power class - it's replaced by Bloc in models.py


@dataclass
class Order:
    power: str
    unit_id: str
    action: str
    target: Optional[str] = None


class ConvictionGame:
    """Main game class with Trust, Alliances, and AI Ladder"""

    AI_LADDER = ("Digital Transformation", "Predictive Analytics", "AI Nexus")

    def __init__(self):
        self.powers: Dict[str, Bloc] = {}
        self.provinces: Dict[str, Province] = {}
        self.units: Dict[str, Unit] = {}
        self.turn = 0
        self.phase = "Spring"
        self.orders: List[Order] = []
        self.last_results = []
        self.power_projections = {}
        self.victory_threshold = 100

    def create_simple_map(self):
        """Create a simple diamond-shaped map"""
        provinces_data = [
            ("North", ["West", "East"], True, 2, 0),
            ("West", ["North", "South"], True, 0, 2),
            ("East", ["North", "South"], True, 4, 2),
            ("South", ["West", "East"], True, 2, 4),
        ]

        for name, adjacents, is_sc, x, y in provinces_data:
            province = Province(name, adjacents, is_sc, x=x, y=y)
            self.provinces[name] = province

        # Create two powers using new Bloc class
        red = Bloc("Red", colour="R")
        blue = Bloc("Blue", colour="B")

        self.powers["Red"] = red
        self.powers["Blue"] = blue

        # Set initial control
        self.provinces["North"].controller = "Red"
        self.provinces["West"].controller = "Red"
        self.provinces["East"].controller = "Blue"
        self.provinces["South"].controller = "Blue"

        # Place starting units
        self.units["R1"] = Unit("R1", "Army", "Red", "North")
        self.units["R2"] = Unit("R2", "Army", "Red", "West")
        self.units["B1"] = Unit("B1", "Army", "Blue", "East")
        self.units["B2"] = Unit("B2", "Army", "Blue", "South")

    def add_alliance(self, p1: str, p2: str) -> None:
        """Creates a mutual alliance edge and gives both sides a soft-power bump."""
        if p1 == p2:
            return

        self.powers[p1].alliances.add(p2)
        self.powers[p2].alliances.add(p1)

        # Small immediate reward for diplomacy
        self.powers[p1].cultural_influence = min(
            10, self.powers[p1].cultural_influence + 1
        )
        self.powers[p2].cultural_influence = min(
            10, self.powers[p2].cultural_influence + 1
        )

        self.last_results.append(
            f"Alliance formed: {p1} ↔ {p2} (+1 Cultural Influence each)"
        )

    def break_alliance(self, p1: str, p2: str) -> None:
        """Break an alliance with conviction penalty."""
        if p2 in self.powers[p1].alliances:
            self.powers[p1].alliances.remove(p2)
            self.powers[p2].alliances.remove(p1)

            # Betrayal penalty
            self.powers[p1].cohesion = max(0, self.powers[p1].cohesion - 2)
            self.powers[p2].cohesion = max(0, self.powers[p2].cohesion - 1)

            self.last_results.append(
                f"Alliance broken: {p1} X {p2} ({p1} -2 Cohesion, {p2} -1 Cohesion)"
            )

    def calculate_power_projection(self, power_name: str) -> int:
        power = self.powers[power_name]

        # Territory & military
        supply_centers = sum(
            1
            for p in self.provinces.values()
            if p.is_supply_center and p.controller == power_name
        )
        units = sum(1 for u in self.units.values() if u.owner == power_name)

        territorial = supply_centers * 15
        military = units * 10
        cohesion_bonus = power.cohesion * 2
        cultural_influence = power.cultural_influence * 3
        tech_bonus = power.tech_bonus()

        # NEW: network bonus = 2 pts per alliance edge
        network_bonus = len(power.alliances) * 2

        total = (
            territorial
            + military
            + cohesion_bonus
            + cultural_influence
            + tech_bonus
            + network_bonus
        )

        # Keep the breakdown for display
        self.power_projections[power_name] = {
            "total": total,
            "territorial": territorial,
            "military": military,
            "cohesion": cohesion_bonus,
            "cultural_influence": cultural_influence,
            "tech": tech_bonus,
            "network": network_bonus,
        }
        return total

    def draw_map(self):
        """Draw ASCII art map"""
        grid = [[" " for _ in range(7)] for _ in range(6)]

        for prov_name, prov in self.provinces.items():
            x, y = prov.x, prov.y
            name_short = prov_name[:3].upper()

            if prov.controller:
                control = f"[{prov.controller[0]}]"
            else:
                control = "[ ]"

            grid[y][x] = name_short
            if y + 1 < len(grid):
                grid[y + 1][x] = control

        print("\n" + "=" * 30)
        print("     CONVICTION MAP")
        print("=" * 30)

        for row in grid:
            print("  " + "".join(row))

        # Show alliances
        print("\nAlliances:")
        for power_name, power in self.powers.items():
            if power.alliances:
                allies = ", ".join(power.alliances)
                print(f"  {power_name} ↔ {allies}")

        print("=" * 30)

    def draw_power_projection_bar(self):
        """Visual representation of power balance"""
        print("\nPOWER PROJECTION BALANCE:")
        print("-" * 50)

        # Calculate projections
        red_power = self.calculate_power_projection("Red")
        blue_power = self.calculate_power_projection("Blue")
        total_power = red_power + blue_power

        # Create visual bar
        bar_width = 40
        if total_power > 0:
            red_width = int((red_power / total_power) * bar_width)
            blue_width = bar_width - red_width
        else:
            red_width = blue_width = bar_width // 2

        # Display bar
        bar = "R" * red_width + "B" * blue_width
        print(f"[{bar}]")
        print(
            f"Red: {red_power:3.0f} pts {'*WIN*' if red_power >= self.victory_threshold else ''}"
        )
        print(
            f"Blue: {blue_power:3.0f} pts {'*WIN*' if blue_power >= self.victory_threshold else ''}"
        )
        print(f"Victory Threshold: {self.victory_threshold} points")
        print("-" * 50)

    def show_power_details(self):
        """Show detailed breakdown of power projection"""
        print("\nPOWER PROJECTION DETAILS:")
        print("-" * 50)

        for power_name in ["Red", "Blue"]:
            proj = self.power_projections.get(power_name, {})
            power = self.powers[power_name]

            tech_level_name = (
                f"Level {power.tech_level}" if power.tech_level > 0 else "None"
            )

            print(f"\n{power_name} (Tech Level: {tech_level_name}):")
            print(f"  Territorial Control: {proj.get('territorial', 0):3.0f} pts")
            print(f"  Military Strength:   {proj.get('military', 0):3.0f} pts")
            print(
                f"  Cohesion Bonus:      {proj.get('cohesion', 0):3.0f} pts (Cohesion: {power.cohesion})"
            )
            print(
                f"  Cultural Influence:  {proj.get('cultural_influence', 0):3.0f} pts (CI: {power.cultural_influence})"
            )
            print(
                f"  Tech Level Bonus:    {proj.get('tech', 0):3.0f} pts (Level {power.tech_level}/3)"
            )
            print(
                f"  Network Bonus:       {proj.get('network', 0):3.0f} pts ({len(power.alliances)} allies)"
            )
            print("  ---")
            print(f"  Trust Score:         {power.trust_score}")
            print(f"  Regulatory Drag:     {power.regulatory_drag}")
            print(f"  Effective Drag:      {power.effective_drag()}")
            print("  ---")
            print(f"  TOTAL:              {proj.get('total', 0):3.0f} pts")

    def show_units(self):
        """Display unit positions"""
        print("\nUNIT POSITIONS:")
        print("-" * 30)
        for prov_name in ["North", "West", "East", "South"]:
            units_here = [u for u in self.units.values() if u.location == prov_name]
            if units_here:
                unit_str = ", ".join([f"{u.owner} {u.type}" for u in units_here])
                print(f"{prov_name:10} -> {unit_str}")
            else:
                print(f"{prov_name:10} -> (empty)")

    def get_valid_moves(self, unit: Unit) -> List[str]:
        """Get list of provinces a unit can move to"""
        current_prov = self.provinces[unit.location]
        return ["Hold"] + current_prov.adjacent_provinces

    def get_human_orders(self, power_name: str) -> List[Order]:
        """Interactive order input for human player"""
        orders = []
        power_units = [u for u in self.units.values() if u.owner == power_name]

        print(f"\n{power_name}'s turn - Issue orders:")
        print("-" * 30)

        # Movement orders
        for unit in power_units:
            valid_moves = self.get_valid_moves(unit)

            print(f"\n{unit.owner} {unit.type} in {unit.location}")
            print("Can move to:", ", ".join(valid_moves))

            while True:
                choice = input("Enter destination (or 'Hold'): ").strip()
                if choice in valid_moves:
                    if choice != "Hold":
                        orders.append(Order(power_name, unit.unit_id, "move", choice))
                    else:
                        orders.append(Order(power_name, unit.unit_id, "hold"))
                    break
                else:
                    print(f"Invalid choice. Options: {', '.join(valid_moves)}")

        # AI Integration attempt
        power = self.powers[power_name]
        if power.tech_level < 3:
            next_stage = self.AI_LADDER[power.tech_level]
            threshold = 4 + power.effective_drag() + power.tech_level

            print("\nAI Integration Status:")
            print(f"  Current Stage: {power.tech_level}/3")
            print(f"  Next Stage: {next_stage}")
            print(f"  Effective Drag: {power.effective_drag()}")
            print(f"  Success threshold: {threshold}/10")

            attempt = input("Attempt AI advancement? (y/n): ")
            if attempt.lower() == "y":
                orders.append(Order(power_name, "AI", "integrate"))

        # Diplomatic actions
        print("\nDiplomatic Actions:")
        other_powers = [p for p in self.powers.keys() if p != power_name]

        for other in other_powers:
            if other in power.alliances:
                break_it = input(f"Break alliance with {other}? (y/n): ")
                if break_it.lower() == "y":
                    self.break_alliance(power_name, other)
            else:
                form_it = input(f"Form alliance with {other}? (y/n): ")
                if form_it.lower() == "y":
                    self.add_alliance(power_name, other)

        return orders

    def _resolve_ai_orders(self, ai_orders: List[Order]) -> None:
        """
        Handle 'integrate' orders, advancing a power by one rung if successful.
        Success threshold = 4 + effective_friction + current_stage
        Roll >= threshold on a d10 succeeds.
        """
        for order in ai_orders:
            power = self.powers[order.power]

            if power.tech_level >= 3:
                self.last_results.append(
                    f"{order.power}: already at the AI Nexus (stage 3)."
                )
                continue

            next_stage_name = self.AI_LADDER[power.tech_level]
            threshold = 4 + power.effective_drag() + power.tech_level
            roll = random.randint(1, 10)

            if roll >= threshold:
                power.tech_level += 1
                power.regulatory_drag += 1  # organizational growing pains

                # Stage-specific bonuses
                if power.tech_level == 1:
                    power.cultural_influence = min(10, power.cultural_influence + 1)
                elif power.tech_level == 2:
                    power.trust_score = min(10, power.trust_score + 1)
                elif power.tech_level == 3:
                    power.cohesion = min(10, power.cohesion + 1)

                self.last_results.append(
                    f"{order.power} advanced to {next_stage_name}! "
                    f"(roll {roll} >= {threshold})"
                )
            else:
                power.regulatory_drag += 1  # failed attempt still hurts
                self.last_results.append(
                    f"{order.power} failed {next_stage_name} "
                    f"(roll {roll} < {threshold}); Regulatory Drag +1"
                )

    def resolve_orders(self, all_orders: List[Order]):
        """Process all orders and resolve conflicts"""
        self.last_results = []

        # Separate order types
        ai_orders = [o for o in all_orders if o.action == "integrate"]
        move_orders = [o for o in all_orders if o.action == "move"]

        # Process AI integration attempts
        self._resolve_ai_orders(ai_orders)

        # Check for movement conflicts
        destinations = defaultdict(list)
        for order in move_orders:
            destinations[order.target].append(order)

        # Resolve movements
        for destination, orders in destinations.items():
            if len(orders) == 1:
                order = orders[0]
                unit = self.units[order.unit_id]
                old_location = unit.location
                unit.location = destination
                self.last_results.append(
                    f"{order.power} Army: {old_location} -> {destination}"
                )
            else:
                for order in orders:
                    unit = self.units[order.unit_id]
                    self.last_results.append(
                        f"{order.power} Army bounced trying to enter {destination}"
                    )

        # Update control
        self.update_control()

        # Random events
        self.process_random_events()

    def process_random_events(self):
        """Random events based on power scores"""
        for power_name, power in self.powers.items():
            # Low cohesion might cause desertion
            if power.cohesion <= 2 and random.random() < 0.2:
                self.last_results.append(f"{power_name}: Low cohesion causing unrest!")
                power.cultural_influence = max(0, power.cultural_influence - 1)

            # High cultural influence might provide benefits
            if power.cultural_influence >= 8 and random.random() < 0.3:
                self.last_results.append(
                    f"{power_name}: High cultural influence attracts support!"
                )
                power.cohesion = min(10, power.cohesion + 1)

            # Low trust creates problems
            if power.trust_score <= 2 and random.random() < 0.3:
                self.last_results.append(
                    f"{power_name}: Low trust causing institutional decay!"
                )
                power.regulatory_drag += 1

    def update_control(self):
        """Update which power controls each province"""
        for prov in self.provinces.values():
            if prov.is_supply_center:
                occupiers = [u for u in self.units.values() if u.location == prov.name]
                if occupiers:
                    prov.controller = occupiers[0].owner

    def check_victory(self) -> Optional[str]:
        """Check if any power has reached victory threshold"""
        for power_name in self.powers:
            if self.calculate_power_projection(power_name) >= self.victory_threshold:
                return power_name
        return None

    def get_game_state_json(self, for_power: str) -> dict:
        """Get game state as JSON for a specific power (for bots/LLMs)"""
        return {
            "turn": self.turn,
            "phase": self.phase,
            "current_power": for_power,
            "map": {name: prov.to_dict() for name, prov in self.provinces.items()},
            "units": {uid: unit.to_dict() for uid, unit in self.units.items()},
            "powers": {name: power.to_dict() for name, power in self.powers.items()},
            "valid_moves": {
                unit.unit_id: self.get_valid_moves(unit)
                for unit in self.units.values()
                if unit.owner == for_power
            },
        }

    def parse_bot_orders(self, power_name: str, orders_json: list) -> List[Order]:
        """Parse orders from bot/LLM format"""
        orders = []
        for order_dict in orders_json:
            if order_dict.get("action") == "move":
                orders.append(
                    Order(
                        power=power_name,
                        unit_id=order_dict["unit_id"],
                        action="move",
                        target=order_dict["target"],
                    )
                )
            elif order_dict.get("action") == "hold":
                orders.append(
                    Order(
                        power=power_name, unit_id=order_dict["unit_id"], action="hold"
                    )
                )
            elif order_dict.get("action") == "integrate":
                orders.append(Order(power=power_name, unit_id="AI", action="integrate"))
            elif order_dict.get("action") == "ally":
                self.add_alliance(power_name, order_dict["target"])
            elif order_dict.get("action") == "break_alliance":
                self.break_alliance(power_name, order_dict["target"])
        return orders

    def get_game_state_json(self, for_power: str) -> dict:
        """Get game state as JSON for a specific power (for bots/LLMs)"""
        return {
            "turn": self.turn,
            "phase": self.phase,
            "current_power": for_power,
            "map": {name: prov.to_dict() for name, prov in self.provinces.items()},
            "units": {uid: unit.to_dict() for uid, unit in self.units.items()},
            "powers": {name: power.to_dict() for name, power in self.powers.items()},
            "valid_moves": {
                unit.unit_id: self.get_valid_moves(unit)
                for unit in self.units.values()
                if unit.owner == for_power
            },
        }

    def parse_bot_orders(self, power_name: str, orders_json: list) -> List[Order]:
        """Parse orders from bot/LLM format"""
        orders = []
        for order_dict in orders_json:
            if order_dict.get("action") == "move":
                orders.append(
                    Order(
                        power=power_name,
                        unit_id=order_dict["unit_id"],
                        action="move",
                        target=order_dict["target"],
                    )
                )
            elif order_dict.get("action") == "hold":
                orders.append(
                    Order(
                        power=power_name, unit_id=order_dict["unit_id"], action="hold"
                    )
                )
            elif order_dict.get("action") == "integrate":
                orders.append(Order(power=power_name, unit_id="AI", action="integrate"))
            elif order_dict.get("action") == "ally":
                self.add_alliance(power_name, order_dict["target"])
            elif order_dict.get("action") == "break_alliance":
                self.break_alliance(power_name, order_dict["target"])
        return orders

    def play_turn(self, bot_strategies=None):
        """Execute one game turn"""
        if bot_strategies is None:
            bot_strategies = {}

        self.turn += 1
        print(f"\n{'='*50}")
        print(f"TURN {self.turn} - {self.phase}")
        print("=" * 50)

        # Show current state
        self.draw_map()
        self.draw_power_projection_bar()
        self.show_units()
        self.show_power_details()

        # Show last turn's results
        if self.last_results:
            print("\nLast Turn Results:")
            for result in self.last_results:
                print(f"  - {result}")

        # Collect orders from all powers
        all_orders = []
        for power_name in self.powers:
            if bot_strategies and power_name in bot_strategies:
                # Bot player
                state = self.get_game_state_json(power_name)
                bot_orders_json = bot_strategies[power_name](state)
                orders = self.parse_bot_orders(power_name, bot_orders_json)
                print(f"\n{power_name} (BOT) orders submitted")
            else:
                # Human player
                orders = self.get_human_orders(power_name)
            all_orders.extend(orders)

        # Resolve all orders
        self.resolve_orders(all_orders)

        # Check for victory
        winner = self.check_victory()
        if winner:
            print(f"\n{'*'*50}")
            print(f"GAME OVER! {winner} achieves dominance!")
            print(
                f"Final Power Projection: {self.calculate_power_projection(winner):.0f}"
            )
            print(f"{'*'*50}")
            return False

        return True


# Bot strategy functions
def random_bot_strategy(game_state: dict) -> list:
    """Simple random bot that sometimes moves, sometimes holds"""
    import random

    orders = []

    power_name = game_state["current_power"]
    valid_moves = game_state["valid_moves"]

    for unit_id, moves in valid_moves.items():
        if random.random() < 0.7:  # 70% chance to move
            target = random.choice(moves)
            if target == "Hold":
                orders.append({"unit_id": unit_id, "action": "hold"})
            else:
                orders.append({"unit_id": unit_id, "action": "move", "target": target})
        else:
            orders.append({"unit_id": unit_id, "action": "hold"})

    # 30% chance to attempt AI integration
    power = game_state["powers"][power_name]
    if power["tech_level"] < 3 and random.random() < 0.3:
        orders.append({"action": "integrate"})

    return orders


def main():
    """Main game loop"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Conviction v2.0: The Three-Bloc Geopolitics Game"
    )
    parser.add_argument(
        "--bot",
        nargs=2,
        action="append",
        metavar=("POWER", "STRATEGY"),
        help="Add bot player: --bot Red random",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without interactive input (requires all players to be bots)",
    )

    args = parser.parse_args()

    print("CONVICTION v2.0: The Three-Bloc Geopolitics Game")
    print("=" * 50)
    print("NEW FEATURES:")
    print("  - Trust Score: Reduces effective drag")
    print("  - Alliance Networks: +2 points per alliance")
    print("  - Tech Ladder: 3 levels of technological advancement")
    print("=" * 50)
    print("\nGoal: Reach 100 Power Projection points")
    print("\nPower comes from:")
    print("  - Territory (15 pts per supply center)")
    print("  - Military (10 pts per unit)")
    print("  - Cohesion (2 pts per point)")
    print("  - Cultural Influence (3 pts per point)")
    print("  - Tech Levels (1/2/5 pts cumulative)")
    print("  - Alliance Networks (2 pts per alliance)")
    print("=" * 50)

    game = ConvictionGame()
    game.create_simple_map()

    # Set up bot strategies if specified
    bot_strategies = {}
    if args.bot:
        for power, strategy in args.bot:
            if strategy == "random":
                bot_strategies[power] = random_bot_strategy
            else:
                print(f"Unknown bot strategy: {strategy}")
                return

    # Validate headless mode
    if args.headless and len(bot_strategies) < len(game.powers):
        print("Error: Headless mode requires all players to be bots")
        return

    # Game loop
    continue_game = True
    while continue_game:
        continue_game = game.play_turn(bot_strategies=bot_strategies)
        if continue_game and not args.headless:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

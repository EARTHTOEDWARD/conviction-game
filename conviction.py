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

# Import the new Bloc class
from models import Bloc, CardType, COUNTER_TABLE, CARD_EFFECTS
from events import draw_random_event, draw_global_event, should_trigger_global_event

# Unit class commented out - replaced by new architecture
# @dataclass
# class Unit:
#     unit_id: str
#     type: str
#     owner: str
#     location: str
#
#     def __repr__(self):
#         return f"{self.owner[0]}{self.type[0]}"
#
#     def to_dict(self):
#         return {
#             'id': self.unit_id,
#             'type': self.type,
#             'owner': self.owner,
#             'location': self.location
#         }


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


TURN_STEPS = (
    "BACK_CHANNEL",  # players negotiate off-board
    "POLICY_DRAFT",  # allocate GDP & choose one card
    "RESOLUTION",  # simultaneous reveal and effects
    "HEADLINE",  # global random event
)


class ConvictionGame:
    """Main game class with Trust, Alliances, and AI Ladder"""

    TURN_STEPS = (
        "BACK_CHANNEL",  # players negotiate off-board
        "POLICY_DRAFT",  # allocate GDP & choose one card
        "RESOLUTION",  # simultaneous reveal and effects
        "HEADLINE",  # global random event
    )

    def __init__(self):
        self.powers: Dict[str, Bloc] = {}
        self.provinces: Dict[str, Province] = {}
        # self.units: Dict[str, Unit] = {}  # Commented out - removing unit movement
        self.turn = 0
        self.phase = "Spring"
        self.orders: List[Order] = []
        self.last_results = []
        self.power_projections = {}
        self.victory_threshold = 50  # New victory point threshold

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

        # Place starting units - COMMENTED OUT FOR NEW ARCHITECTURE
        # self.units["R1"] = Unit("R1", "Army", "Red", "North")
        # self.units["R2"] = Unit("R2", "Army", "Red", "West")
        # self.units["B1"] = Unit("B1", "Army", "Blue", "East")
        # self.units["B2"] = Unit("B2", "Army", "Blue", "South")

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
        # units = sum(1 for u in self.units.values() if u.owner == power_name)  # COMMENTED OUT

        territorial = supply_centers * 15
        # military = units * 10  # COMMENTED OUT
        military = 0  # No units in new architecture
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
        """Visual representation of power balance using new victory point system"""
        print("\nVICTORY POINT BALANCE:")
        print("-" * 50)

        # Calculate victory points using new system
        red_vp = self.powers["Red"].bloc_vp()
        blue_vp = self.powers["Blue"].bloc_vp()
        total_vp = red_vp + blue_vp

        # Create visual bar
        bar_width = 40
        if total_vp > 0:
            red_width = int((red_vp / total_vp) * bar_width)
            blue_width = bar_width - red_width
        else:
            red_width = blue_width = bar_width // 2

        # Display bar
        bar = "R" * red_width + "B" * blue_width
        print(f"[{bar}]")
        print(
            f"Red: {red_vp:3.0f} VP {'*WIN*' if red_vp >= self.victory_threshold else ''}"
        )
        print(
            f"Blue: {blue_vp:3.0f} VP {'*WIN*' if blue_vp >= self.victory_threshold else ''}"
        )
        print(f"Victory Threshold: {self.victory_threshold} victory points")
        print("-" * 50)

    def show_power_details(self):
        """Show detailed breakdown of victory points"""
        print("\nVICTORY POINTS DETAILS:")
        print("-" * 50)

        for power_name in ["Red", "Blue"]:
            power = self.powers[power_name]

            tech_level_name = (
                f"Level {power.tech_level}" if power.tech_level > 0 else "None"
            )
            total_vp = power.bloc_vp()

            print(f"\n{power_name} (Tech Level: {tech_level_name}):")
            print(f"  GDP Tokens:          {power.gdp_tokens:3.0f} VP")
            print(
                f"  Tech Level Bonus:    {power.tech_bonus():3.0f} VP (Level {power.tech_level}/3)"
            )
            print(
                f"  Military Posture:    {power.military_posture * 2:3.0f} VP (Posture: {power.military_posture})"
            )
            print(f"  Cultural Influence:  {power.cultural_influence:3.0f} VP")
            print(f"  Cohesion:            {power.cohesion:3.0f} VP")
            print(
                f"  Satellite States:    {len(power.satellites) * 3:3.0f} VP ({len(power.satellites)} satellites)"
            )
            print(
                f"  Alliance Network:    {len(power.alliances) * 2:3.0f} VP ({len(power.alliances)} allies)"
            )
            print(
                f"  Regulatory Drag:     -{power.effective_drag():3.0f} VP (Effective: {power.effective_drag()})"
            )
            print("  ---")
            print(f"  Trust Score:         {power.trust_score}")
            print(f"  Raw Regulatory Drag: {power.regulatory_drag}")
            print("  ---")
            print(f"  TOTAL VICTORY POINTS: {total_vp:3.0f} VP")

    # def show_units(self):
    #     """Display unit positions"""
    #     print("\nUNIT POSITIONS:")
    #     print("-"*30)
    #     for prov_name in ["North", "West", "East", "South"]:
    #         units_here = [u for u in self.units.values() if u.location == prov_name]
    #         if units_here:
    #             unit_str = ", ".join([f"{u.owner} {u.type}" for u in units_here])
    #             print(f"{prov_name:10} -> {unit_str}")
    #         else:
    #             print(f"{prov_name:10} -> (empty)")

    # def get_valid_moves(self, unit: Unit) -> List[str]:
    #     """Get list of provinces a unit can move to"""
    #     current_prov = self.provinces[unit.location]
    #     return ["Hold"] + current_prov.adjacent_provinces

    def get_human_orders(self, power_name: str) -> List[Order]:
        """Interactive order input for human player"""
        orders = []
        # power_units = [u for u in self.units.values() if u.owner == power_name]  # COMMENTED OUT

        print(f"\n{power_name}'s turn - Issue orders:")
        print("-" * 30)

        # Movement orders - COMMENTED OUT FOR NEW ARCHITECTURE
        # for unit in power_units:
        #     valid_moves = self.get_valid_moves(unit)
        #
        #     print(f"\n{unit.owner} {unit.type} in {unit.location}")
        #     print("Can move to:", ", ".join(valid_moves))
        #
        #     while True:
        #         choice = input("Enter destination (or 'Hold'): ").strip()
        #         if choice in valid_moves:
        #             if choice != "Hold":
        #                 orders.append(Order(power_name, unit.unit_id, "move", choice))
        #             else:
        #                 orders.append(Order(power_name, unit.unit_id, "hold"))
        #             break
        #         else:
        #             print(f"Invalid choice. Options: {', '.join(valid_moves)}")

        # Diplomatic actions
        power = self.powers[power_name]
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

    def resolve_orders(self, all_orders: List[Order]):
        """Process all orders and resolve conflicts"""
        self.last_results = []

        # Note: AI integration now handled through budget spending in technology category
        # Movement conflicts are not applicable in new architecture

        # Update control
        self.update_control()

        # Random events
        self.process_random_events()
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
                # occupiers = [u for u in self.units.values() if u.location == prov.name]  # COMMENTED OUT
                # if occupiers:
                #     prov.controller = occupiers[0].owner
                pass  # No unit-based control in new architecture

    def check_victory(self) -> Optional[str]:
        """Check if any bloc has reached victory threshold using new bloc_vp system"""
        for power_name in self.powers:
            bloc_victory_points = self.powers[power_name].bloc_vp()
            if bloc_victory_points >= self.victory_threshold:
                return power_name
        return None

    def get_game_state_json(self, for_power: str) -> dict:
        """Get game state as JSON for a specific power (for bots/LLMs)"""
        return {
            "turn": self.turn,
            "phase": self.phase,
            "current_power": for_power,
            "map": {name: prov.to_dict() for name, prov in self.provinces.items()},
            # "units": {uid: unit.to_dict() for uid, unit in self.units.items()},  # COMMENTED OUT
            "powers": {name: power.to_dict() for name, power in self.powers.items()},
            # "valid_moves": {  # COMMENTED OUT FOR NEW ARCHITECTURE
            #     unit.unit_id: self.get_valid_moves(unit)
            #     for unit in self.units.values()
            #     if unit.owner == for_power
            # }
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
            elif order_dict.get("action") == "ally":
                self.add_alliance(power_name, order_dict["target"])
            elif order_dict.get("action") == "break_alliance":
                self.break_alliance(power_name, order_dict["target"])
        return orders

    def _back_channel(self):
        """Phase 1: Back channel negotiations (off-board diplomacy)"""
        print("\n--- PHASE 1: BACK CHANNEL ---")
        print("Players may negotiate alliances, deals, and agreements privately.")
        # TODO: Implement back-channel negotiation mechanics

    def _policy_draft(self, bot_strategies=None):
        """Phase 2: Policy draft (allocate GDP & choose cards)"""
        print("\n--- PHASE 2: POLICY DRAFT ---")
        print("Players allocate GDP tokens and select policy cards.")

        # First, generate GDP income for all blocs
        self._generate_gdp_income()

        # Show current state for decision making
        self.draw_map()
        self.draw_power_projection_bar()
        self.show_power_details()

        # Show last turn's results
        if self.last_results:
            print("\nLast Turn Results:")
            for result in self.last_results:
                print(f"  - {result}")

        # Collect budget allocations and orders from all powers
        all_orders = []
        for power_name in self.powers:
            if bot_strategies and power_name in bot_strategies:
                # Bot player - for now use simplified budget allocation
                self._handle_bot_budget_allocation(power_name)
                state = self.get_game_state_json(power_name)
                bot_orders_json = bot_strategies[power_name](state)
                orders = self.parse_bot_orders(power_name, bot_orders_json)
                print(f"\n{power_name} (BOT) orders submitted")
            else:
                # Human player
                self._handle_human_budget_allocation(power_name)
                orders = self.get_human_orders(power_name)
            all_orders.extend(orders)

        # Store orders for resolution phase
        self.orders = all_orders

    def _generate_gdp_income(self):
        """Generate GDP income for all blocs based on their economic development and territories."""
        print("\n=== GDP INCOME GENERATION ===")

        for power_name, power in self.powers.items():
            # Count controlled supply centers
            controlled_territories = sum(
                1
                for p in self.provinces.values()
                if p.is_supply_center and p.controller == power_name
            )

            # Generate income
            income = power.generate_gdp_income(controlled_territories)
            old_gdp = power.gdp_tokens
            power.gdp_tokens += income

            print(f"{power_name}: Generated {income} GDP tokens")
            print("  Base income: 3")
            print(
                f"  Territory bonus: {controlled_territories * 2} ({controlled_territories} territories)"
            )
            print(f"  Development bonus: {power.economic_development}")
            print(f"  Cohesion bonus: {max(0, power.cohesion - 3)}")
            print(f"  Drag penalty: -{power.effective_drag()}")
            print(f"  Total GDP: {old_gdp} → {power.gdp_tokens}")

    def _handle_human_budget_allocation(self, power_name: str):
        """Handle budget allocation for human players."""
        power = self.powers[power_name]

        print(f"\n=== {power_name.upper()} BUDGET ALLOCATION ===")
        print(f"Available GDP Tokens: {power.gdp_tokens}")
        print(f"Economic Development Level: {power.economic_development}")

        if power.gdp_tokens <= 0:
            print("No GDP tokens available for allocation this turn.")
            return

        print("\nBudget Categories:")
        print("  1. Military     - Increase Military Posture")
        print("  2. Technology   - Advance Tech Level")
        print("  3. Culture      - Increase Cultural Influence")
        print("  4. Infrastructure - Improve Economic Development & reduce Drag")
        print("  5. Diplomacy    - Increase Trust Score")

        allocations = {}
        remaining = power.gdp_tokens

        categories = [
            "military",
            "technology",
            "culture",
            "infrastructure",
            "diplomacy",
        ]

        for category in categories:
            if remaining <= 0:
                allocations[category] = 0
                continue

            while True:
                try:
                    allocation = int(input(f"Allocate to {category} (0-{remaining}): "))
                    if 0 <= allocation <= remaining:
                        allocations[category] = allocation
                        remaining -= allocation
                        break
                    else:
                        print(f"Invalid allocation. Must be between 0 and {remaining}.")
                except ValueError:
                    print("Please enter a valid number.")

        # Show final allocation
        print("\nFinal Budget Allocation:")
        total_spent = 0
        for category, amount in allocations.items():
            if amount > 0:
                print(f"  {category.capitalize()}: {amount}")
                total_spent += amount

        print(f"Total Spent: {total_spent}/{power.gdp_tokens}")
        print(f"Remaining: {power.gdp_tokens - total_spent}")

        # Confirm allocation
        confirm = input("Confirm allocation? (y/n): ").lower()
        if confirm == "y":
            success = power.allocate_budget(allocations)
            if success:
                print("Budget allocated successfully!")
            else:
                print("Error: Budget allocation failed!")
        else:
            print("Budget allocation cancelled. No spending this turn.")

        # Card selection
        self._handle_human_card_selection(power_name)

    def _handle_bot_budget_allocation(self, power_name: str):
        """Handle simple budget allocation for bot players."""
        power = self.powers[power_name]

        if power.gdp_tokens <= 0:
            return

        # Simple bot strategy: prioritize based on current weaknesses
        allocations = {
            "military": 0,
            "technology": 0,
            "culture": 0,
            "infrastructure": 0,
            "diplomacy": 0,
        }
        remaining = power.gdp_tokens

        # Priority order based on current state
        priorities = []

        # Tech advancement if we're behind
        if power.tech_level < 2:
            priorities.append(("technology", min(3, remaining)))

        # Military if weak
        if power.military_posture < 3:
            priorities.append(("military", min(2, remaining)))

        # Infrastructure if high drag
        if power.effective_drag() > 2:
            priorities.append(("infrastructure", min(3, remaining)))

        # Culture if low
        if power.cultural_influence < 3:
            priorities.append(("culture", min(2, remaining)))

        # Diplomacy if low trust
        if power.trust_score < 4:
            priorities.append(("diplomacy", min(2, remaining)))

        # Allocate based on priorities
        for category, amount in priorities:
            if remaining <= 0:
                break
            actual_amount = min(amount, remaining)
            allocations[category] = actual_amount
            remaining -= actual_amount

        # Spend any remaining on military (default)
        if remaining > 0:
            allocations["military"] += remaining

        power.allocate_budget(allocations)
        print(f"{power_name} (BOT): Allocated budget - {allocations}")

        # Bot card selection
        self._handle_bot_card_selection(power_name)

    def _handle_human_card_selection(self, power_name: str):
        """Handle card selection for human players."""
        power = self.powers[power_name]

        print(f"\n=== {power_name.upper()} CARD SELECTION ===")
        print("Choose a policy card to play this turn:")

        cards = list(CardType)
        for i, card in enumerate(cards, 1):
            effect_desc = CARD_EFFECTS[card]["description"]
            counter_card = COUNTER_TABLE[card]
            print(f"  {i:2d}. {card.name:<20} - {effect_desc}")
            print(f"      (Countered by: {counter_card.name})")

        while True:
            try:
                choice = int(input(f"Select card (1-{len(cards)}): "))
                if 1 <= choice <= len(cards):
                    selected_card = cards[choice - 1]
                    power.chosen_card = selected_card
                    print(f"Selected: {selected_card.name}")
                    break
                else:
                    print(f"Invalid choice. Must be between 1 and {len(cards)}.")
            except ValueError:
                print("Please enter a valid number.")

    def _handle_bot_card_selection(self, power_name: str):
        """Handle simple card selection for bot players."""
        power = self.powers[power_name]

        # Simple bot strategy: random card selection for now
        # TODO: Implement smarter bot card selection based on opponent's likely choices
        available_cards = list(CardType)
        selected_card = random.choice(available_cards)
        power.chosen_card = selected_card

        print(f"{power_name} (BOT): Selected card - {selected_card.name}")

    def _resolution(self):
        """Phase 3: Resolution (simultaneous reveal and effects)"""
        print("\n--- PHASE 3: RESOLUTION ---")
        print("All orders are revealed and resolved simultaneously.")

        # First, apply budget spending effects
        self._apply_budget_spending()

        # Then resolve card interactions
        self._resolve_card_interactions()

        # Then process the orders collected in policy draft phase
        self.resolve_orders(self.orders)

    def _apply_budget_spending(self):
        """Apply the effects of budget spending for all blocs."""
        print("\n=== BUDGET SPENDING EFFECTS ===")

        for power_name, power in self.powers.items():
            spending_results = power.spend_budget()

            if spending_results:
                print(f"\n{power_name} spending results:")
                for result in spending_results:
                    print(f"  - {result}")
                    self.last_results.append(f"{power_name}: {result}")
            else:
                print(f"\n{power_name}: No budget allocated this turn.")

    def _resolve_card_interactions(self):
        """Resolve card interactions between all blocs."""
        print("\n=== CARD RESOLUTION ===")

        # Display all chosen cards
        print("Cards played this turn:")
        for power_name, power in self.powers.items():
            if power.chosen_card:
                print(f"  {power_name}: {power.chosen_card.name}")
            else:
                print(f"  {power_name}: No card selected")

        # Resolve pairwise interactions
        power_names = list(self.powers.keys())
        for i, power1_name in enumerate(power_names):
            for power2_name in power_names[i + 1 :]:
                self._resolve_card_pair(power1_name, power2_name)

        # Clear cards after resolution
        for power in self.powers.values():
            power.chosen_card = None

    def _resolve_card_pair(self, power1_name: str, power2_name: str):
        """Resolve card interaction between two specific powers."""
        power1 = self.powers[power1_name]
        power2 = self.powers[power2_name]

        card1 = power1.chosen_card
        card2 = power2.chosen_card

        if not card1 or not card2:
            return  # Skip if either player didn't select a card

        print(f"\n{power1_name} ({card1.name}) vs {power2_name} ({card2.name}):")

        # Check for counters
        power1_countered = card2 == COUNTER_TABLE[card1]
        power2_countered = card1 == COUNTER_TABLE[card2]

        if power1_countered and power2_countered:
            print("  Both cards counter each other - no effect!")
            self.last_results.append(
                f"Card battle: {power1_name} vs {power2_name} - mutual counter!"
            )
        elif power1_countered:
            print(
                f"  {power2_name}'s {card2.name} counters {power1_name}'s {card1.name}!"
            )
            self._apply_card_effect(power2_name, power1_name, card2)
            self.last_results.append(
                f"Card battle: {power2_name}'s {card2.name} counters {power1_name}'s {card1.name}"
            )
        elif power2_countered:
            print(
                f"  {power1_name}'s {card1.name} counters {power2_name}'s {card2.name}!"
            )
            self._apply_card_effect(power1_name, power2_name, card1)
            self.last_results.append(
                f"Card battle: {power1_name}'s {card1.name} counters {power2_name}'s {card2.name}"
            )
        else:
            print("  No counters - both cards take effect!")
            self._apply_card_effect(power1_name, power2_name, card1)
            self._apply_card_effect(power2_name, power1_name, card2)
            self.last_results.append(
                f"Card battle: {power1_name} and {power2_name} both succeed"
            )

    def _apply_card_effect(self, attacker_name: str, target_name: str, card: CardType):
        """Apply the effect of a successful card play."""
        attacker = self.powers[attacker_name]
        target = self.powers[target_name]
        effect_type = CARD_EFFECTS[card]["effect"]

        if effect_type == "steal_tech":
            if target.tech_level > attacker.tech_level:
                attacker.tech_level = min(3, attacker.tech_level + 1)
                target.tech_level = max(0, target.tech_level - 1)
                print(f"    {attacker_name} steals tech from {target_name}!")
                self.last_results.append(
                    f"{attacker_name}: Cyber espionage successful - tech level +1"
                )
                self.last_results.append(f"{target_name}: Tech stolen - tech level -1")

        elif effect_type == "reduce_gdp":
            reduction = min(3, target.gdp_tokens)
            target.gdp_tokens = max(0, target.gdp_tokens - reduction)
            print(f"    {target_name} loses {reduction} GDP tokens from tariffs!")
            self.last_results.append(
                f"{target_name}: Tariff damage - lost {reduction} GDP tokens"
            )

        elif effect_type == "boost_military":
            attacker.military_posture = min(5, attacker.military_posture + 1)
            print(f"    {attacker_name} gains military advantage!")
            self.last_results.append(
                f"{attacker_name}: Proxy arms successful - military posture +1"
            )

        elif effect_type == "increase_drag":
            target.regulatory_drag = min(10, target.regulatory_drag + 2)
            print(f"    {target_name} suffers increased regulatory burden!")
            self.last_results.append(
                f"{target_name}: Standards pressure - regulatory drag +2"
            )

        elif effect_type == "reduce_cohesion":
            target.cohesion = max(0, target.cohesion - 1)
            target.trust_score = max(0, target.trust_score - 1)
            print(f"    {target_name} suffers from disinformation campaign!")
            self.last_results.append(
                f"{target_name}: Disinformation damage - cohesion -1, trust -1"
            )

        elif effect_type == "boost_trust":
            attacker.trust_score = min(5, attacker.trust_score + 1)
            attacker.regulatory_drag = max(0, attacker.regulatory_drag - 1)
            print(f"    {attacker_name} improves intelligence capabilities!")
            self.last_results.append(
                f"{attacker_name}: Counter-intel success - trust +1, drag -1"
            )

        elif effect_type == "boost_economy":
            attacker.gdp_tokens = min(20, attacker.gdp_tokens + 2)
            attacker.cultural_influence = min(5, attacker.cultural_influence + 1)
            print(f"    {attacker_name} benefits from trade deal!")
            self.last_results.append(
                f"{attacker_name}: Trade deal success - GDP +2, cultural influence +1"
            )

        elif effect_type == "boost_influence":
            attacker.cohesion = min(5, attacker.cohesion + 1)
            # TODO: Add satellite influence mechanics when implemented
            print(f"    {attacker_name} gains regional influence!")
            self.last_results.append(
                f"{attacker_name}: Aid/reconstruction success - cohesion +1"
            )

        elif effect_type == "boost_lobbying":
            attacker.regulatory_drag = max(0, attacker.regulatory_drag - 1)
            attacker.cultural_influence = min(5, attacker.cultural_influence + 1)
            print(f"    {attacker_name} succeeds in lobbying efforts!")
            self.last_results.append(
                f"{attacker_name}: Lobbying success - drag -1, cultural influence +1"
            )

        elif effect_type == "boost_moderation":
            attacker.cohesion = min(5, attacker.cohesion + 1)
            attacker.cultural_influence = min(5, attacker.cultural_influence + 1)
            print(f"    {attacker_name} improves content moderation!")
            self.last_results.append(
                f"{attacker_name}: Content moderation success - cohesion +1, cultural influence +1"
            )

    def _headline_news(self):
        """Phase 4: Headline news (global random events)"""
        print("\n--- PHASE 4: HEADLINE NEWS ---")

        # Check for global events first
        if should_trigger_global_event():
            global_event = draw_global_event()
            print(f"\n🌍 GLOBAL EVENT: {global_event.name}")
            print(f"   {global_event.description}")

            # Apply to all blocs
            for power_name, power in self.powers.items():
                global_event.effect(power, self)

            print("   Global event affects all blocs!")
        else:
            # Draw individual events for each bloc
            print("\n📰 Regional Events:")

            for power_name, power in self.powers.items():
                # 60% chance each bloc gets an event
                if random.random() < 0.6:
                    event = draw_random_event()
                    print(f"\n   {power_name}: {event.name}")
                    print(f"   → {event.description}")
                    event.effect(power, self)
                else:
                    print(f"\n   {power_name}: Quiet turn, no major events")

        print("\n--- End of Headline News ---")

    def play_turn(self, bot_strategies=None):
        """Execute one game turn with four phases"""
        if bot_strategies is None:
            bot_strategies = {}

        self.turn += 1
        print(f"\n{'='*50}")
        print(f"TURN {self.turn}")
        print("=" * 50)

        # Phase 1: Back Channel
        self.phase = self.TURN_STEPS[0]  # start at back-channel
        self._back_channel()

        # Phase 2: Policy Draft
        self.phase = self.TURN_STEPS[1]
        self._policy_draft(bot_strategies)

        # Phase 3: Resolution
        self.phase = self.TURN_STEPS[2]
        self._resolution()

        # Phase 4: Headline
        self.phase = self.TURN_STEPS[3]
        self._headline_news()

        # Check for victory
        winner = self.check_victory()
        if winner:
            winner_vp = self.powers[winner].bloc_vp()
            print(f"\n{'*'*50}")
            print(f"GAME OVER! {winner} achieves dominance!")
            print(f"Final Victory Points: {winner_vp:.0f} VP")
            print(f"{'*'*50}")
            return False

        return True


# Bot strategy functions
def random_bot_strategy(game_state: dict) -> list:
    """Simple random bot that sometimes moves, sometimes holds"""
    orders = []

    game_state["current_power"]
    # valid_moves = game_state["valid_moves"]  # COMMENTED OUT FOR NEW ARCHITECTURE

    # Movement logic commented out - no units in new architecture
    # for unit_id, moves in valid_moves.items():
    #     if random.random() < 0.7:  # 70% chance to move
    #         target = random.choice(moves)
    #         if target == "Hold":
    #             orders.append({"unit_id": unit_id, "action": "hold"})
    #         else:
    #             orders.append({"unit_id": unit_id, "action": "move", "target": target})
    #     else:
    #         orders.append({"unit_id": unit_id, "action": "hold"})

    # 30% chance to attempt AI integration - REMOVED: Now handled by budget allocation
    # power = game_state["powers"][power_name]
    # if power["tech_level"] < 3 and random.random() < 0.3:
    #     orders.append({"action": "integrate"})

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
    print("  - Alliance Networks: +2 victory points per alliance")
    print("  - Tech Ladder: 3 levels of technological advancement")
    print("  - Victory Point System: Win by reaching threshold")
    print("  - GDP Budgeting: Allocate resources across domains")
    print("  - Card System: Rock-paper-scissors policy interactions")
    print("=" * 50)
    print("\nGoal: Reach 50 Victory Points")
    print("\nVictory Points come from:")
    print("  - GDP Tokens (1 VP each)")
    print("  - Tech Levels (1/2/5 VP cumulative)")
    print("  - Military Posture (2 VP per level)")
    print("  - Cultural Influence (1 VP per point)")
    print("  - Cohesion (1 VP per point)")
    print("  - Satellite States (3 VP each)")
    print("  - Alliance Networks (2 VP per alliance)")
    print("  - Regulatory Drag penalty (-1 VP per effective drag)")
    print("=" * 50)
    print("\nEach turn has 4 phases:")
    print("  1. Back Channel: Private negotiations")
    print("  2. Policy Draft: Allocate GDP & select policy card")
    print("  3. Resolution: Budget spending & card battles")
    print("  4. Headline News: Global random events")
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

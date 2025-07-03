#!/usr/bin/env python3
"""
Conviction Enhanced: Geopolitical Strategy Game with Targeted Policy Cards
Version 3.0: Three-Bloc Competition with Realistic Leverage Mechanics

Implements targeting system where policy cards can target specific opponents
or multiple opponents at increased cost.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import random

from models import (
    Bloc, CardType, Target, Domain, PolicyCard, Move,
    COUNTER_TABLE, CARD_EFFECTS, POLICY_CARDS, SIGNATURE_DOMAIN,
    TechLevel, ProxyRegion
)
from events import draw_random_event, draw_global_event, should_trigger_global_event


class ConvictionEnhancedGame:
    """Enhanced game with targeting mechanics and expanded geopolitical options."""
    
    def __init__(self, three_bloc_mode: bool = True):
        self.powers: Dict[str, Bloc] = {}
        self.turn = 0
        self.phase = "Spring"
        self.last_results = []
        self.victory_threshold = 50
        self.three_bloc_mode = three_bloc_mode
        
        # Track moves for resolution
        self.current_moves: Dict[str, Move] = {}
        
        # Initialize blocs
        if three_bloc_mode:
            self._create_three_bloc_game()
        else:
            self._create_simple_game()
    
    def _create_three_bloc_game(self):
        """Create USA, EU, and China blocs."""
        usa = Bloc("USA", colour="U")
        eu = Bloc("EU", colour="E") 
        china = Bloc("China", colour="C")
        
        # Set initial lever levels based on historical strengths
        usa.lever_level = 2  # Strong financial dominance
        eu.lever_level = 1   # Moderate regulatory power
        china.lever_level = 2  # Strong trade position
        
        self.powers = {
            "USA": usa,
            "EU": eu,
            "China": china
        }
    
    def _create_simple_game(self):
        """Create simple two-player game."""
        red = Bloc("Red", colour="R")
        blue = Bloc("Blue", colour="B")
        
        self.powers = {
            "Red": red,
            "Blue": blue
        }
    
    def compute_card_cost(self, bloc: Bloc, move: Move) -> int:
        """Calculate actual GDP cost after lever discounts & multi-target premium."""
        card = move.card
        cost = card.base_cost
        
        # Multi-target costs 2x
        if Target.BOTH in move.targets:
            cost *= 2
        
        # Discount if using signature lever domain
        if card.domain == bloc.get_signature_domain():
            cost = max(0, cost - bloc.lever_level)
        
        return cost
    
    def can_afford_move(self, bloc: Bloc, move: Move) -> bool:
        """Check if bloc can afford the move."""
        cost = self.compute_card_cost(bloc, move)
        return bloc.gdp_tokens >= cost
    
    def distribute_card_effect(self, attacker: Bloc, target: Bloc, card: PolicyCard, is_multi_target: bool):
        """Apply card effect to target, with reduced effect if multi-targeting."""
        effect_type = CARD_EFFECTS[card.card_type]["effect"]
        
        # Halve effects if targeting multiple opponents
        multiplier = 0.5 if is_multi_target else 1.0
        
        if effect_type == "steal_tech":
            if target.tech_level > attacker.tech_level:
                gain = int(1 * multiplier + 0.5)  # Round up
                attacker.tech_level = min(3, attacker.tech_level + gain)
                target.tech_level = max(0, target.tech_level - gain)
                self.last_results.append(
                    f"{attacker.name} steals {gain} tech from {target.name}"
                )
        
        elif effect_type == "reduce_gdp":
            reduction = int(3 * multiplier + 0.5)
            actual_reduction = min(reduction, target.gdp_tokens)
            target.gdp_tokens = max(0, target.gdp_tokens - actual_reduction)
            self.last_results.append(
                f"{target.name} loses {actual_reduction} GDP from tariffs"
            )
        
        elif effect_type == "financial_sanctions":
            gdp_freeze = int(3 * multiplier + 0.5)
            dev_damage = int(1 * multiplier + 0.5)
            target.gdp_tokens = max(0, target.gdp_tokens - gdp_freeze)
            target.economic_development = max(0, target.economic_development - dev_damage)
            self.last_results.append(
                f"{target.name} hit by sanctions: -{gdp_freeze} GDP, -{dev_damage} development"
            )
        
        elif effect_type == "secondary_sanctions":
            # Force allies to join sanctions in next turn
            target.regulatory_drag += int(2 * multiplier + 0.5)
            self.last_results.append(
                f"{target.name} faces secondary sanctions pressure: +{int(2 * multiplier + 0.5)} drag"
            )
        
        elif effect_type == "dumping":
            dev_damage = int(2 * multiplier + 0.5)
            target.economic_development = max(0, target.economic_development - dev_damage)
            self.last_results.append(
                f"{target.name} damaged by dumping: -{dev_damage} economic development"
            )
        
        elif effect_type == "tech_transfer":
            # Special case: only works on allies (not enemies)
            if target in attacker.alliances:
                tech_gain = int(1 * multiplier + 0.5)
                attacker.tech_level = min(3, attacker.tech_level + tech_gain)
                target.tech_level = min(3, target.tech_level + tech_gain)
                self.last_results.append(
                    f"Tech transfer: {attacker.name} and {target.name} both gain {tech_gain} tech"
                )
        
        elif effect_type == "export_controls":
            # Block tech advancement for multiple turns
            tech_penalty = int(2 * multiplier + 0.5)
            target.regulatory_drag += tech_penalty
            self.last_results.append(
                f"{target.name} hit by export controls: +{tech_penalty} tech advancement cost"
            )
        
        elif effect_type == "rare_earth_embargo":
            tech_damage = int(1 * multiplier + 0.5)
            military_damage = int(1 * multiplier + 0.5)
            target.tech_level = max(0, target.tech_level - tech_damage)
            target.military_posture = max(0, target.military_posture - military_damage)
            self.last_results.append(
                f"{target.name} embargoed: -{tech_damage} tech, -{military_damage} military"
            )
        
        elif effect_type == "regulatory_clampdown":
            drag_increase = int(3 * multiplier + 0.5)
            target.regulatory_drag += drag_increase
            self.last_results.append(
                f"{target.name} faces regulatory assault: +{drag_increase} drag"
            )
        
        elif effect_type == "carbon_tariff":
            # Tax unless target has high infrastructure
            if target.economic_development < 3:
                tax = int(2 * multiplier + 0.5)
                target.gdp_tokens = max(0, target.gdp_tokens - tax)
                self.last_results.append(
                    f"{target.name} pays carbon tax: -{tax} GDP"
                )
            else:
                self.last_results.append(
                    f"{target.name} avoids carbon tax (green infrastructure)"
                )
        
        # Apply original card effects with multiplier
        elif effect_type == "boost_military":
            gain = int(1 * multiplier + 0.5)
            attacker.military_posture = min(5, attacker.military_posture + gain)
            self.last_results.append(f"{attacker.name} gains {gain} military posture")
        
        elif effect_type == "increase_drag":
            increase = int(2 * multiplier + 0.5)
            target.regulatory_drag = min(10, target.regulatory_drag + increase)
            self.last_results.append(f"{target.name} gains {increase} regulatory drag")
        
        elif effect_type == "reduce_cohesion":
            cohesion_loss = int(1 * multiplier + 0.5)
            trust_loss = int(1 * multiplier + 0.5)
            target.cohesion = max(0, target.cohesion - cohesion_loss)
            target.trust_score = max(0, target.trust_score - trust_loss)
            self.last_results.append(
                f"{target.name} loses {cohesion_loss} cohesion, {trust_loss} trust"
            )
        
        # Self-targeting effects
        elif effect_type in ["boost_trust", "boost_economy", "boost_influence", 
                           "boost_lobbying", "boost_moderation", "anti_dumping"]:
            self._apply_self_effect(attacker, effect_type, multiplier)
    
    def _apply_self_effect(self, bloc: Bloc, effect_type: str, multiplier: float):
        """Apply effects that benefit the caster."""
        if effect_type == "boost_trust":
            trust_gain = int(1 * multiplier + 0.5)
            drag_reduction = int(1 * multiplier + 0.5)
            bloc.trust_score = min(5, bloc.trust_score + trust_gain)
            bloc.regulatory_drag = max(0, bloc.regulatory_drag - drag_reduction)
            self.last_results.append(
                f"{bloc.name}: +{trust_gain} trust, -{drag_reduction} drag"
            )
        
        elif effect_type == "boost_economy":
            gdp_gain = int(2 * multiplier + 0.5)
            culture_gain = int(1 * multiplier + 0.5)
            bloc.gdp_tokens = min(20, bloc.gdp_tokens + gdp_gain)
            bloc.cultural_influence = min(5, bloc.cultural_influence + culture_gain)
            self.last_results.append(
                f"{bloc.name}: +{gdp_gain} GDP, +{culture_gain} cultural influence"
            )
        
        elif effect_type == "anti_dumping":
            # Defensive boost
            gdp_gain = int(1 * multiplier + 0.5)
            bloc.gdp_tokens = min(20, bloc.gdp_tokens + gdp_gain)
            bloc.economic_development = min(5, bloc.economic_development + 1)
            self.last_results.append(
                f"{bloc.name} protects economy: +{gdp_gain} GDP, +1 development"
            )
    
    def _policy_draft_phase(self):
        """Enhanced policy draft phase with targeting."""
        print("\n--- PHASE 2: POLICY DRAFT ---")
        print("Allocate GDP, select policy cards, and choose targets.")
        
        # Generate GDP income
        for power_name, power in self.powers.items():
            income = power.generate_gdp_income()
            power.gdp_tokens += income
            print(f"{power_name} generates {income} GDP (Total: {power.gdp_tokens})")
        
        # Show current state
        self._show_game_state()
        
        # Collect moves from each power
        for power_name, power in self.powers.items():
            print(f"\n=== {power_name} TURN ===")
            
            # Budget allocation
            self._handle_budget_allocation(power_name)
            
            # Card and target selection
            self._handle_card_selection_with_targets(power_name)
    
    def _handle_card_selection_with_targets(self, power_name: str):
        """Handle card selection with target choice."""
        power = self.powers[power_name]
        
        print(f"\n{power_name} - Select Policy Card and Targets")
        print(f"Available GDP: {power.gdp_tokens}")
        print(f"Signature Domain: {power.get_signature_domain().value if power.get_signature_domain() else 'None'}")
        print(f"Lever Level: {power.lever_level}")
        
        # Show available cards with costs
        cards = list(CardType)
        print("\nAvailable Policy Cards:")
        for i, card_type in enumerate(cards, 1):
            card = POLICY_CARDS[card_type]
            effect_desc = CARD_EFFECTS[card_type]["description"]
            
            # Calculate costs for different targeting options
            single_cost = card.base_cost
            if card.domain == power.get_signature_domain():
                single_cost = max(0, single_cost - power.lever_level)
            
            both_cost = card.base_cost * 2
            if card.domain == power.get_signature_domain():
                both_cost = max(0, both_cost - power.lever_level)
            
            print(f"  {i:2d}. {card_type.name:<25} ({card.domain.value})")
            print(f"      {effect_desc}")
            print(f"      Cost: {single_cost} GDP (single) / {both_cost} GDP (both)")
        
        # Select card
        while True:
            try:
                choice = int(input(f"\nSelect card (1-{len(cards)}): "))
                if 1 <= choice <= len(cards):
                    selected_card_type = cards[choice - 1]
                    selected_card = POLICY_CARDS[selected_card_type]
                    break
                else:
                    print(f"Invalid choice. Must be between 1 and {len(cards)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Select targets
        print(f"\nSelected: {selected_card_type.name}")
        print("Choose target(s):")
        
        other_powers = [p for p in self.powers.keys() if p != power_name]
        print("  1. " + other_powers[0])
        if len(other_powers) > 1:
            print("  2. " + other_powers[1])
            print("  3. Both opponents")
        
        while True:
            try:
                target_choice = int(input("Select target: "))
                if target_choice == 1:
                    targets = [Target(other_powers[0])]
                elif len(other_powers) > 1 and target_choice == 2:
                    targets = [Target(other_powers[1])]
                elif len(other_powers) > 1 and target_choice == 3:
                    targets = [Target.BOTH]
                else:
                    print("Invalid target choice.")
                    continue
                
                # Create move and check affordability
                move = Move(card=selected_card, targets=targets)
                cost = self.compute_card_cost(power, move)
                
                if cost > power.gdp_tokens:
                    print(f"Cannot afford this move! Cost: {cost}, Available: {power.gdp_tokens}")
                    print("Please select a different card or target.")
                    continue
                
                # Confirm and store move
                print(f"Total cost: {cost} GDP")
                power.gdp_tokens -= cost
                self.current_moves[power_name] = move
                power.chosen_card = selected_card_type
                power.chosen_targets = targets
                break
                
            except ValueError:
                print("Please enter a valid number.")
    
    def _resolution_phase(self):
        """Enhanced resolution phase with targeted effects."""
        print("\n--- PHASE 3: RESOLUTION ---")
        
        # Apply budget spending
        for power_name, power in self.powers.items():
            results = power.spend_budget()
            if results:
                print(f"\n{power_name} budget effects:")
                for result in results:
                    print(f"  - {result}")
                    self.last_results.append(f"{power_name}: {result}")
        
        # Resolve card interactions with targeting
        print("\n=== CARD RESOLUTION ===")
        
        # Show all moves
        print("\nMoves this turn:")
        for power_name, move in self.current_moves.items():
            targets_str = ", ".join([t.value for t in move.targets])
            print(f"  {power_name}: {move.card.card_type.name} -> {targets_str}")
        
        # Process each move
        for attacker_name, move in self.current_moves.items():
            attacker = self.powers[attacker_name]
            
            # Determine actual targets
            if Target.BOTH in move.targets:
                actual_targets = [name for name in self.powers.keys() if name != attacker_name]
            else:
                actual_targets = [t.value for t in move.targets if t != Target.BOTH]
            
            for target_name in actual_targets:
                if target_name in self.powers:
                    target = self.powers[target_name]
                    
                    # Check if target has a counter
                    target_move = self.current_moves.get(target_name)
                    if target_move and target_move.card.card_type == COUNTER_TABLE.get(move.card.card_type):
                        # Check if the counter targets the attacker
                        counter_targets = []
                        if Target.BOTH in target_move.targets:
                            counter_targets = [n for n in self.powers.keys() if n != target_name]
                        else:
                            counter_targets = [t.value for t in target_move.targets]
                        
                        if attacker_name in counter_targets:
                            print(f"\n{target_name}'s {target_move.card.card_type.name} counters "
                                  f"{attacker_name}'s {move.card.card_type.name}!")
                            self.last_results.append(
                                f"{target_name} counters {attacker_name}'s attack"
                            )
                            continue
                    
                    # Apply effect
                    is_multi = Target.BOTH in move.targets
                    print(f"\n{attacker_name}'s {move.card.card_type.name} hits {target_name}")
                    self.distribute_card_effect(attacker, target, move.card, is_multi)
        
        # Clear moves
        self.current_moves.clear()
        for power in self.powers.values():
            power.chosen_card = None
            power.chosen_targets = []
    
    def _handle_budget_allocation(self, power_name: str):
        """Handle budget allocation for a power."""
        power = self.powers[power_name]
        
        print(f"\n{power_name} Budget Allocation")
        print(f"Available GDP: {power.gdp_tokens}")
        
        if power.gdp_tokens == 0:
            print("No GDP to allocate!")
            return
        
        allocations = {}
        categories = ["military", "technology", "culture", "infrastructure", "diplomacy"]
        
        remaining = power.gdp_tokens
        for category in categories:
            if remaining <= 0:
                allocations[category] = 0
                continue
                
            while True:
                try:
                    amount = int(input(f"{category.capitalize()} (0-{remaining}): "))
                    if 0 <= amount <= remaining:
                        allocations[category] = amount
                        remaining -= amount
                        break
                    else:
                        print(f"Invalid amount. Must be between 0 and {remaining}.")
                except ValueError:
                    print("Please enter a valid number.")
        
        if power.allocate_budget(allocations):
            print("Budget allocated successfully!")
        else:
            print("Budget allocation failed!")
    
    def _show_game_state(self):
        """Display current game state."""
        print("\n=== CURRENT GAME STATE ===")
        print(f"Turn {self.turn}")
        
        for power_name, power in self.powers.items():
            vp = power.bloc_vp()
            print(f"\n{power_name}:")
            print(f"  Victory Points: {vp}/{self.victory_threshold}")
            print(f"  GDP: {power.gdp_tokens}, Tech: {power.tech_level}, Military: {power.military_posture}")
            print(f"  Lever: {power.lever_level}, Trust: {power.trust_score}, Drag: {power.regulatory_drag}")
    
    def _headline_phase(self):
        """Process random events."""
        print("\n--- PHASE 4: HEADLINE NEWS ---")
        
        # Global events
        if should_trigger_global_event():
            event = draw_global_event()
            print(f"\nGLOBAL EVENT: {event.name}")
            print(f"{event.description}")
            
            for power in self.powers.values():
                event.apply_to_bloc(power)
                self.last_results.append(f"Global: {event.name} affects {power.name}")
        
        # Individual events
        for power_name, power in self.powers.items():
            if random.random() < 0.3:  # 30% chance
                event = draw_random_event()
                print(f"\n{power_name}: {event.name}")
                event.apply_to_bloc(power)
                self.last_results.append(f"{power_name}: {event.name}")
    
    def check_victory(self) -> Optional[str]:
        """Check if any bloc has achieved victory."""
        for power_name, power in self.powers.items():
            if power.bloc_vp() >= self.victory_threshold:
                return power_name
        return None
    
    def run_turn(self):
        """Run a complete game turn."""
        self.turn += 1
        print(f"\n{'='*60}")
        print(f"TURN {self.turn}")
        print(f"{'='*60}")
        
        # Phase 1: Back channel (diplomacy)
        print("\n--- PHASE 1: BACK CHANNEL ---")
        print("Players may negotiate privately.")
        # Could add alliance formation/breaking here
        
        # Phase 2: Policy draft
        self._policy_draft_phase()
        
        # Phase 3: Resolution
        self._resolution_phase()
        
        # Phase 4: Headlines
        self._headline_phase()
        
        # Check victory
        winner = self.check_victory()
        if winner:
            print(f"\n{'='*60}")
            print(f"GAME OVER! {winner} achieves victory!")
            print(f"{'='*60}")
            return False
        
        return True


def main():
    """Run the enhanced game."""
    print("CONVICTION: Enhanced Geopolitical Strategy Game")
    print("="*50)
    
    # Game mode selection
    print("\nSelect game mode:")
    print("1. Three-bloc game (USA, EU, China)")
    print("2. Simple two-player game")
    
    while True:
        try:
            mode = int(input("Choose mode (1-2): "))
            if mode == 1:
                game = ConvictionEnhancedGame(three_bloc_mode=True)
                break
            elif mode == 2:
                game = ConvictionEnhancedGame(three_bloc_mode=False)
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Run game
    while game.run_turn():
        input("\nPress Enter to continue to next turn...")
    
    # Final scores
    print("\nFINAL SCORES:")
    for power_name, power in game.powers.items():
        print(f"{power_name}: {power.bloc_vp()} Victory Points")


if __name__ == "__main__":
    main()
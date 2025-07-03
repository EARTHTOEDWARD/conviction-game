#!/usr/bin/env python3
"""
Demo script showing the enhanced targeting mechanics in action.
"""

from models import (
    Bloc, CardType, Target, Domain, PolicyCard, Move,
    POLICY_CARDS, SIGNATURE_DOMAIN
)
from conviction_enhanced import ConvictionEnhancedGame


def demo_targeting_system():
    """Demonstrate the targeting mechanics."""
    print("=== CONVICTION ENHANCED: Targeting System Demo ===\n")
    
    # Create game with three blocs
    game = ConvictionEnhancedGame(three_bloc_mode=True)
    
    # Get the blocs
    usa = game.powers["USA"]
    eu = game.powers["EU"]
    china = game.powers["China"]
    
    print("Initial State:")
    print(f"USA: {usa.gdp_tokens} GDP, Lever {usa.lever_level} (Finance)")
    print(f"EU: {eu.gdp_tokens} GDP, Lever {eu.lever_level} (Regulation)")
    print(f"China: {china.gdp_tokens} GDP, Lever {china.lever_level} (Trade)")
    
    # Demonstrate cost calculations
    print("\n--- Cost Calculation Examples ---")
    
    # Example 1: USA using Financial Sanctions
    sanctions_card = POLICY_CARDS[CardType.FINANCIAL_SANCTIONS]
    
    # Single target
    single_move = Move(card=sanctions_card, targets=[Target.CHINA])
    single_cost = game.compute_card_cost(usa, single_move)
    print(f"\nUSA -> Financial Sanctions -> China")
    print(f"  Base cost: {sanctions_card.base_cost} GDP")
    print(f"  USA has Finance lever {usa.lever_level}: -{usa.lever_level} discount")
    print(f"  Final cost: {single_cost} GDP")
    
    # Multi target
    multi_move = Move(card=sanctions_card, targets=[Target.BOTH])
    multi_cost = game.compute_card_cost(usa, multi_move)
    print(f"\nUSA -> Financial Sanctions -> Both (EU & China)")
    print(f"  Base cost: {sanctions_card.base_cost} GDP")
    print(f"  Multi-target multiplier: x2")
    print(f"  USA has Finance lever {usa.lever_level}: -{usa.lever_level} discount")
    print(f"  Final cost: {multi_cost} GDP")
    
    # Example 2: EU using Regulatory Clampdown
    reg_card = POLICY_CARDS[CardType.REGULATORY_CLAMPDOWN]
    
    single_move = Move(card=reg_card, targets=[Target.USA])
    single_cost = game.compute_card_cost(eu, single_move)
    print(f"\nEU -> Regulatory Clampdown -> USA")
    print(f"  Base cost: {reg_card.base_cost} GDP")
    print(f"  EU has Regulation lever {eu.lever_level}: -{eu.lever_level} discount")
    print(f"  Final cost: {single_cost} GDP")
    
    # Example 3: China using Import Ban (Tariff Hike)
    tariff_card = POLICY_CARDS[CardType.TARIFF_HIKE]
    
    single_move = Move(card=tariff_card, targets=[Target.USA])
    single_cost = game.compute_card_cost(china, single_move)
    print(f"\nChina -> Tariff Hike -> USA")
    print(f"  Base cost: {tariff_card.base_cost} GDP")
    print(f"  China has Trade lever {china.lever_level}: -{china.lever_level} discount")
    print(f"  Final cost: {single_cost} GDP")
    
    # Demonstrate effect distribution
    print("\n\n--- Effect Distribution Examples ---")
    
    # Reset some values for demo
    usa.gdp_tokens = 10
    eu.gdp_tokens = 10
    china.gdp_tokens = 10
    
    print("\nScenario 1: USA sanctions China only")
    sanctions_move = Move(card=sanctions_card, targets=[Target.CHINA])
    cost = game.compute_card_cost(usa, sanctions_move)
    print(f"Cost: {cost} GDP")
    print("Effect: China loses 3 GDP and 1 economic development")
    
    print("\nScenario 2: USA sanctions both EU and China")
    sanctions_both = Move(card=sanctions_card, targets=[Target.BOTH])
    cost = game.compute_card_cost(usa, sanctions_both)
    print(f"Cost: {cost} GDP (doubled)")
    print("Effect: Both EU and China lose 2 GDP and 1 development (halved, rounded up)")
    
    print("\nScenario 3: Counter example")
    print("USA plays Financial Sanctions -> China")
    print("China plays Trade Deal (counters Financial Sanctions)")
    print("Result: China's Trade Deal blocks USA's sanctions!")
    
    # Show advanced cards
    print("\n\n--- New Geopolitical Cards ---")
    
    advanced_cards = [
        (CardType.SECONDARY_SANCTIONS, "Force allies to join your sanctions"),
        (CardType.DUMPING_PRODUCTS, "Damage opponent's economic base"),
        (CardType.TECH_TRANSFER, "Share technology with allies"),
        (CardType.EXPORT_CONTROLS, "Block opponent's tech advancement"),
        (CardType.RARE_EARTH_EMBARGO, "Cripple tech and military production"),
        (CardType.CARBON_TARIFF, "Tax opponents unless they go green"),
    ]
    
    for card_type, desc in advanced_cards:
        card = POLICY_CARDS[card_type]
        print(f"\n{card_type.name}")
        print(f"  Domain: {card.domain.value}")
        print(f"  Base Cost: {card.base_cost} GDP")
        print(f"  Effect: {desc}")


def demo_turn_sequence():
    """Show a sample turn with the new mechanics."""
    print("\n\n=== Sample Turn Sequence ===\n")
    
    # Create game
    game = ConvictionEnhancedGame(three_bloc_mode=True)
    
    # Set up initial state
    usa = game.powers["USA"]
    eu = game.powers["EU"] 
    china = game.powers["China"]
    
    # Give everyone some GDP to work with
    usa.gdp_tokens = 8
    eu.gdp_tokens = 8
    china.gdp_tokens = 8
    
    print("Turn 1 - Policy Selection")
    print("------------------------")
    
    # USA move
    usa_card = POLICY_CARDS[CardType.FINANCIAL_SANCTIONS]
    usa_move = Move(card=usa_card, targets=[Target.CHINA])
    usa_cost = game.compute_card_cost(usa, usa_move)
    print(f"USA: Financial Sanctions -> China (Cost: {usa_cost} GDP)")
    
    # EU move  
    eu_card = POLICY_CARDS[CardType.REGULATORY_CLAMPDOWN]
    eu_move = Move(card=eu_card, targets=[Target.BOTH])
    eu_cost = game.compute_card_cost(eu, eu_move)
    print(f"EU: Regulatory Clampdown -> Both (Cost: {eu_cost} GDP)")
    
    # China move
    china_card = POLICY_CARDS[CardType.DUMPING_PRODUCTS]
    china_move = Move(card=china_card, targets=[Target.USA])
    china_cost = game.compute_card_cost(china, china_move)
    print(f"China: Dumping Products -> USA (Cost: {china_cost} GDP)")
    
    print("\nResolution:")
    print("-----------")
    print("1. USA's sanctions hit China: -3 GDP, -1 development")
    print("2. EU's regulations hit both USA and China: +2 regulatory drag each")
    print("3. China's dumping hits USA: -2 economic development")
    
    print("\nEnd State:")
    print("USA: Hit by regulations and dumping")
    print("EU: Spent GDP on multi-target attack")
    print("China: Hit by sanctions and regulations")


if __name__ == "__main__":
    demo_targeting_system()
    demo_turn_sequence()
    
    print("\n\n=== Key Mechanics Summary ===")
    print("1. Each bloc has a signature domain with cost discounts")
    print("2. Cards can target single opponents or 'Both' at 2x cost")
    print("3. Multi-targeting halves the effect on each target")
    print("4. Lever tracks (0-3) provide increasing discounts")
    print("5. New cards model real geopolitical tactics")
    print("\nRun conviction_enhanced.py to play the full game!")
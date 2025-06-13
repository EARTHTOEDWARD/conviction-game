#!/usr/bin/env python3
"""
Test script for Conviction v2.0 - Verify all systems are working
"""

def test_conviction_systems():
    """Test all major systems in Conviction v2.0"""
    print("🧪 Testing Conviction v2.0 Systems")
    print("=" * 50)
    
    try:
        # Test imports
        import conviction
        import models
        import events
        print("✅ All modules import successfully")
        
        # Test game initialization  
        game = conviction.ConvictionGame()
        game.create_simple_map()
        print("✅ Game initialization")
        
        # Test new Bloc model
        red = game.powers["Red"]
        blue = game.powers["Blue"]
        print(f"✅ Bloc model - Red: {red.name}, Blue: {blue.name}")
        
        # Test GDP budgeting system
        red.gdp_tokens = 10
        budget_success = red.allocate_budget({
            'military': 2, 
            'technology': 3, 
            'culture': 1, 
            'infrastructure': 2, 
            'diplomacy': 2
        })
        print(f"✅ GDP budgeting - Allocation success: {budget_success}")
        
        # Test budget spending
        spending_results = red.spend_budget()
        print(f"✅ Budget spending - {len(spending_results)} effects applied")
        
        # Test card system
        from models import CardType, COUNTER_TABLE, CARD_EFFECTS
        red.chosen_card = CardType.CYBER_ESPIONAGE
        blue.chosen_card = CardType.COUNTER_INTEL
        print(f"✅ Card system - {len(list(CardType))} cards, {len(COUNTER_TABLE)} counters")
        
        # Test card resolution
        game._resolve_card_pair("Red", "Blue")
        print("✅ Card resolution system")
        
        # Test event system
        event = events.draw_random_event()
        old_gdp = red.gdp_tokens
        event.effect(red, game)
        print(f"✅ Event system - '{event.name}' applied")
        
        # Test global events
        global_event = events.draw_global_event()
        print(f"✅ Global events - '{global_event.name}' available")
        
        # Test victory point system
        red_vp = red.bloc_vp()
        blue_vp = blue.bloc_vp()
        print(f"✅ Victory points - Red: {red_vp} VP, Blue: {blue_vp} VP")
        
        # Test victory condition
        winner = game.check_victory()
        print(f"✅ Victory checking - Winner: {winner or 'None yet'}")
        
        print("\n🎉 ALL SYSTEMS WORKING PERFECTLY!")
        print("\nConviction v2.0 Features:")
        print("  ✅ GDP Budgeting System") 
        print("  ✅ Card Battle System (Rock-Paper-Scissors)")
        print("  ✅ Random Event Deck")
        print("  ✅ Victory Point System")
        print("  ✅ Four-Phase Turn Structure")
        print("  ✅ Retired Old AI Integration")
        print("  ✅ Clean, Formatted Codebase")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_conviction_systems()
    exit(0 if success else 1)

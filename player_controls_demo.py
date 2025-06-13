# player_controls_demo.py
"""
Demo showing the player control panels in action.
Run this to test the new control interface.
"""

import asyncio
from models import Bloc, ProxyRegion
from web_bridge import ConvictionWebBridge


async def demo_with_controls():
    """Run demo with player controls enabled."""
    
    print("🎮 CONVICTION - Player Controls Demo")
    print("=" * 50)
    
    # Create game state using the proper structure
    class DummyGame:
        def __init__(self):
            self.powers = {
                'USA': Bloc(name='USA', gdp_tokens=10),
                'EU': Bloc(name='EU', gdp_tokens=8), 
                'China': Bloc(name='China', gdp_tokens=12)
            }
            self.provinces = {
                'Arctic Council': type('Province', (), {'name': 'Arctic Council', 'controller': None}),
                'North Atlantic': type('Province', (), {'name': 'North Atlantic', 'controller': 'USA'}),
                'Latin America': type('Province', (), {'name': 'Latin America', 'controller': 'USA'}),
                'Africa': type('Province', (), {'name': 'Africa', 'controller': 'EU'}),
                'Middle East': type('Province', (), {'name': 'Middle East', 'controller': None}),
                'Central Asia': type('Province', (), {'name': 'Central Asia', 'controller': 'China'}),
                'S.E. Asia': type('Province', (), {'name': 'S.E. Asia', 'controller': 'China'}),
                'Pacific Rim': type('Province', (), {'name': 'Pacific Rim', 'controller': None}),
                'Indo-Pacific': type('Province', (), {'name': 'Indo-Pacific', 'controller': None})
            }
            self.turn = 1
            self.phase = 'Planning'
    
    game = DummyGame()
    
    # Start server
    server = ConvictionWebBridge(game)
    
    print("\n✅ Starting server...")
    
    # Run server
    runner = await server.run('localhost', 8080)
    
    await asyncio.sleep(3)
    
    print("\n📋 Instructions:")
    print("1. Open http://localhost:8080 in your browser")
    print("2. Click 'Show Controls' at the bottom of the screen")
    print("3. Each player can allocate their GDP budget:")
    print("   - Military, Technology, Culture, Infrastructure, Diplomacy")
    print("4. Select an action card from the dropdown")
    print("5. Click 'Submit Turn' when ready")
    print("6. Game advances when all 3 players submit\n")
    
    # Simulate game phases
    phases = ['Planning', 'Card Selection', 'Resolution', 'Scoring']
    turn = 1
    
    try:
        while True:
            for phase in phases:
                await server.update_turn_phase(turn, phase)
                print(f"📍 Turn {turn} - {phase} Phase")
                
                if phase == 'Resolution':
                    # Simulate some influence changes
                    await asyncio.sleep(3)
                    await server.update_region('Middle East', 'China', 4)
                    await asyncio.sleep(1)
                    await server.update_region('Pacific Rim', 'USA', 5)
                    print("   ⚔️ Influence contests resolved")
                
                elif phase == 'Scoring':
                    # Update GDP for next turn
                    await asyncio.sleep(2)
                    game.powers['USA'].gdp_tokens += 3
                    game.powers['EU'].gdp_tokens += 2  
                    game.powers['China'].gdp_tokens += 4
                    
                    # Send updated state
                    state = server.serialize_game_state()
                    await server.broadcast_update('game_state', state)
                    print("   💰 GDP income distributed")
                
                await asyncio.sleep(5)
            
            turn += 1
            if turn > 5:
                print("\n🏁 Demo complete after 5 turns!")
                break
        
        print("\nServer running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(demo_with_controls())
    except KeyboardInterrupt:
        print("\nDemo stopped.")

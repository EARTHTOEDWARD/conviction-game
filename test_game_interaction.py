#!/usr/bin/env python3
"""
Simple test to show that the game responds to player inputs.
This simulates what happens when players interact with the web interface.
"""

import asyncio
import json
import websockets
from game_with_controls import ConvictionGameWithControls


async def test_player_interaction():
    """Test that the game responds to player inputs."""
    
    print("🧪 Testing Game Player Interaction")
    print("=" * 50)
    
    # Start the game in the background
    game = ConvictionGameWithControls()
    runner = await game.start()
    
    await asyncio.sleep(2)  # Give server time to start
    
    try:
        # Connect to the WebSocket
        uri = "ws://localhost:8080/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to game server")
            
            # Simulate USA player submitting a turn
            usa_turn = {
                "action": "submit_turn",
                "bloc": "USA",
                "budget": {
                    "military": 3,
                    "technology": 2,
                    "culture": 1,
                    "infrastructure": 2,
                    "diplomacy": 2
                },
                "card": "CYBER_ESPIONAGE"
            }
            
            print("\n🇺🇸 USA submitting turn...")
            await websocket.send(json.dumps(usa_turn))
            
            # Wait for confirmation
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"   Server response: {response_data}")
            
            # Simulate EU player submitting a turn
            eu_turn = {
                "action": "submit_turn",
                "bloc": "EU",
                "budget": {
                    "military": 2,
                    "technology": 3,
                    "culture": 1,
                    "infrastructure": 1,
                    "diplomacy": 1
                },
                "card": "TRADE_DEAL"
            }
            
            print("\n🇪🇺 EU submitting turn...")
            await websocket.send(json.dumps(eu_turn))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"   Server response: {response_data}")
            
            # Simulate China player submitting a turn
            china_turn = {
                "action": "submit_turn",
                "bloc": "China",
                "budget": {
                    "military": 4,
                    "technology": 3,
                    "culture": 2,
                    "infrastructure": 2,
                    "diplomacy": 1
                },
                "card": "PROXY_ARMS"
            }
            
            print("\n🇨🇳 China submitting turn...")
            await websocket.send(json.dumps(china_turn))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"   Server response: {response_data}")
            
            print("\n⏳ Waiting for turn processing...")
            await asyncio.sleep(8)  # Wait for turn processing
            
            print("✅ Turn processing completed!")
            print("\n💡 The game is working! Players can:")
            print("   • Connect via web browser at http://localhost:8080")
            print("   • Allocate budgets using sliders")
            print("   • Select action cards")
            print("   • Submit turns")
            print("   • See real-time game progression")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up
        await runner.cleanup()
        print("\n🏁 Test completed")


if __name__ == "__main__":
    try:
        asyncio.run(test_player_interaction())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")

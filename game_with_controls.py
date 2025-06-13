# game_with_controls.py
"""
Example showing how to integrate player controls with your game logic.
This connects the web UI to your actual game engine.
"""

import asyncio
import json
from typing import Dict
from models import Bloc, ProxyRegion, CardType
from web_bridge import ConvictionWebBridge


class ConvictionGameWithControls:
    """Enhanced game engine that processes player control inputs."""
    
    def __init__(self):
        # Initialize game state
        self.powers = {
            'USA': Bloc(name='USA', gdp_tokens=10),
            'EU': Bloc(name='EU', gdp_tokens=8),
            'China': Bloc(name='China', gdp_tokens=12)
        }
        
        self.provinces = {
            'Arctic Council': type('Province', (), {'name': 'Arctic Council', 'controller': None}),
            'North Atlantic': type('Province', (), {'name': 'North Atlantic', 'controller': None}),
            'Latin America': type('Province', (), {'name': 'Latin America', 'controller': None}),
            'Africa': type('Province', (), {'name': 'Africa', 'controller': None}),
            'Middle East': type('Province', (), {'name': 'Middle East', 'controller': None}),
            'Central Asia': type('Province', (), {'name': 'Central Asia', 'controller': None}),
            'S.E. Asia': type('Province', (), {'name': 'S.E. Asia', 'controller': None}),
            'Pacific Rim': type('Province', (), {'name': 'Pacific Rim', 'controller': None}),
            'Indo-Pacific': type('Province', (), {'name': 'Indo-Pacific', 'controller': None})
        }
        
        self.turn = 1
        self.phase = 'Planning'
        self.turn_submissions = {}
        
        # Web server
        self.web_server = None
    
    async def start(self):
        """Start the game with web visualization."""
        # Create web server with game state
        self.web_server = ConvictionWebBridge(self)
        
        # Override the handle_player_action to use our game logic
        original_handle_player_action = self.web_server.handle_player_action
        self.web_server.handle_player_action = self.handle_player_action
        
        # Start server
        runner = await self.web_server.run('localhost', 8080)
        
        await asyncio.sleep(3)
        print("🎮 Conviction game started!")
        print("📱 Open browser to play: http://localhost:8080")
        
        return runner
    
    async def handle_player_action(self, ws, data):
        """Process player actions from the web UI."""
        action = data.get('action')
        
        if action == 'submit_turn':
            bloc_name = data.get('bloc')
            budget = data.get('budget')
            card = data.get('card')
            
            print(f"\n{bloc_name} submitted:")
            print(f"  Budget: {budget}")
            print(f"  Card: {card}")
            
            # Store submission
            self.turn_submissions[bloc_name] = {
                'budget': budget,
                'card': CardType[card] if card else None
            }
            
            # Apply budget to bloc
            bloc = self.powers[bloc_name]
            bloc.allocate_budget({
                'military': budget.get('military', 0),
                'technology': budget.get('technology', 0),
                'culture': budget.get('culture', 0),
                'infrastructure': budget.get('infrastructure', 0),
                'diplomacy': budget.get('diplomacy', 0)
            })
            bloc.chosen_card = CardType[card] if card else None
            
            # Send confirmation
            await ws.send_str(json.dumps({
                'type': 'turn_submitted',
                'bloc': bloc_name,
                'accepted': True
            }))
            
            # Check if all submitted
            if len(self.turn_submissions) == 3:
                await self.process_turn()
    
    async def process_turn(self):
        """Process the complete turn."""
        print("\n" + "="*50)
        print(f"PROCESSING TURN {self.turn}")
        print("="*50)
        
        # 1. Apply budget spending
        await self.apply_budgets()
        
        # 2. Resolve card plays
        await self.resolve_cards()
        
        # 3. Resolve influence contests
        await self.resolve_influence()
        
        # 4. Generate income
        await self.generate_income()
        
        # 5. Update scores
        await self.update_scores()
        
        # Reset for next turn
        self.turn_submissions = {}
        self.turn += 1
        
        # Update UI
        await self.web_server.update_turn_phase(
            self.turn, 
            'Planning'
        )
        
        # Send updated game state
        state = self.web_server.serialize_game_state()
        await self.web_server.broadcast_update(
            'game_state',
            state
        )
    
    async def apply_budgets(self):
        """Apply budget spending effects."""
        print("\n📊 Applying budgets...")
        
        for bloc_name, bloc in self.powers.items():
            results = bloc.spend_budget()
            if results:
                print(f"\n{bloc_name}:")
                for result in results:
                    print(f"  - {result}")
        
        await asyncio.sleep(2)
    
    async def resolve_cards(self):
        """Resolve card plays."""
        print("\n🎴 Resolving cards...")
        
        # Simple resolution - in real game, handle counters
        for bloc_name, submission in self.turn_submissions.items():
            card = submission.get('card')
            if card:
                print(f"{bloc_name} plays {card.name}")
                # Apply card effects here
        
        await asyncio.sleep(2)
    
    async def resolve_influence(self):
        """Resolve influence contests."""
        print("\n⚔️ Resolving influence...")
        
        # Example: Contest in Middle East
        if self.provinces['Middle East'].controller is None:
            # Calculate influence scores
            scores = {}
            for bloc_name, bloc in self.powers.items():
                scores[bloc_name] = (
                    bloc.military_posture + 
                    (3 if bloc.chosen_card == CardType.PROXY_ARMS else 0)
                )
            
            winner = max(scores, key=scores.get)
            print(f"  Middle East: {winner} wins with score {scores[winner]}")
            
            self.provinces['Middle East'].controller = winner
            await self.web_server.update_region(
                'Middle East',
                winner,
                min(6, scores[winner] // 2)
            )
        
        await asyncio.sleep(3)
    
    async def generate_income(self):
        """Generate GDP income."""
        print("\n💰 Generating income...")
        
        for bloc_name, bloc in self.powers.items():
            # Count controlled regions
            controlled = sum(
                1 for province in self.provinces.values()
                if province.controller == bloc_name
            )
            
            income = bloc.generate_gdp_income(controlled)
            bloc.gdp_tokens += income
            print(f"  {bloc_name}: +{income} GDP (Total: {bloc.gdp_tokens})")
        
        await asyncio.sleep(2)
    
    async def update_scores(self):
        """Calculate and display victory points."""
        print("\n🏆 Victory Points:")
        
        for bloc_name, bloc in self.powers.items():
            vp = bloc.bloc_vp()
            print(f"  {bloc_name}: {vp} VP")
            
            if vp >= 50:
                print(f"\n🎉 {bloc_name} WINS!")
                return True
        
        return False
    
    async def run(self):
        """Run the game loop."""
        runner = await self.start()
        
        # Game continues until interrupted
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\nGame ended by user.")
        finally:
            await runner.cleanup()


# Main execution
async def main():
    game = ConvictionGameWithControls()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())

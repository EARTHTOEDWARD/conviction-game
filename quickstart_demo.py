# quickstart_demo.py - Quick demonstration of Conviction with web visualization
import asyncio
import webbrowser
import time
from conviction import ConvictionGame
from web_bridge import ConvictionWebBridge
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConvictionDemo:
    """Interactive demo of the Conviction game with web visualization."""
    
    def __init__(self):
        self.game = ConvictionGame()
        self.bridge = ConvictionWebBridge(self.game)
        self.running = False
    
    async def start_demo(self):
        """Start the demo with web visualization."""
        print("🌍 CONVICTION 2040 - Interactive Demo")
        print("=" * 50)
        print()
        
        # Start the web server
        print("🚀 Starting web visualization server...")
        runner = await self.bridge.run(host='localhost', port=8080)
        
        # Give the server a moment to start
        await asyncio.sleep(1)
        
        print("✅ Server started at http://localhost:8080")
        print()
        print("🌐 Opening web browser...")
        
        # Open the browser
        try:
            webbrowser.open('http://localhost:8080')
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please manually open: http://localhost:8080")
        
        print()
        print("📋 Demo Instructions:")
        print("- The web page shows an abstract world map")
        print("- Major power blocs (USA, EU, China) are shown as large circles")
        print("- Influence regions are smaller circles with dice indicators")
        print("- Watch for real-time updates as the demo runs")
        print()
        
        self.running = True
        
        try:
            # Run the interactive demo
            await self.run_demo_sequence()
            
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        finally:
            print("\n🔄 Shutting down server...")
            await runner.cleanup()
            print("✅ Demo completed!")
    
    async def run_demo_sequence(self):
        """Run through a sequence of demo actions."""
        print("🎯 Starting demo sequence...")
        print()
        
        # Initialize game
        self.game.create_simple_map()
        await self.update_visualization()
        
        # Demo sequence
        demos = [
            ("Initial Setup", self.demo_initial_state),
            ("Budget Allocation", self.demo_budget_allocation),
            ("Proxy Region Contest", self.demo_proxy_contest),
            ("Technology Development", self.demo_tech_development),
            ("Military Buildup", self.demo_military_buildup),
            ("Final Scoring", self.demo_final_scoring),
        ]
        
        for demo_name, demo_func in demos:
            print(f"📍 {demo_name}")
            print("-" * 30)
            await demo_func()
            await self.update_visualization()
            await self.wait_for_user()
            print()
    
    async def demo_initial_state(self):
        """Show the initial game state."""
        print("🏛️ Three major power blocs compete for global influence:")
        print()
        
        for name, bloc in self.game.powers.items():
            print(f"  {name}:")
            print(f"    💰 GDP: {bloc.gdp_tokens}")
            print(f"    🤝 Cohesion: {bloc.cohesion}")
            print(f"    🔬 Tech Level: {bloc.tech_level}")
            print(f"    ⚔️ Military: {bloc.military_posture}")
            print(f"    🎭 Culture: {bloc.cultural_influence}")
            print()
        
        print("🗺️ Proxy regions start neutral, ready to be influenced...")
    
    async def demo_budget_allocation(self):
        """Demonstrate budget allocation system."""
        print("💼 Each bloc allocates their GDP budget across different priorities:")
        print()
        
        # USA focuses on military and technology
        usa = self.game.powers['Red']
        usa_budget = {"military": 2, "technology": 2, "culture": 1}
        usa.allocate_budget(usa_budget)
        results = usa.spend_budget()
        
        print("🇺🇸 Red Bloc Strategy - Military-Tech Focus:")
        for result in results:
            print(f"    • {result}")
        
        # EU focuses on diplomacy and culture
        eu = self.game.powers['Blue']
        eu_budget = {"diplomacy": 2, "culture": 2, "infrastructure": 1}
        eu.allocate_budget(eu_budget)
        results = eu.spend_budget()
        
        print("\n🇪🇺 Blue Bloc Strategy - Diplomatic-Cultural Focus:")
        for result in results:
            print(f"    • {result}")
        
        print("\n🎯 Each bloc's investments shape their capabilities...")
    
    async def demo_proxy_contest(self):
        """Demonstrate proxy region contests."""
        print("🎲 Blocs compete for influence in proxy regions:")
        print()
        
        # Simulate some region contests
        regions_to_contest = ["North", "South", "East"]
        
        for region_name in regions_to_contest:
            region = self.game.provinces.get(region_name)
            if not region:
                continue
            
            print(f"📍 Contest for {region_name}:")
            
            # Simulate contest outcomes
            import random
            contestants = ["Red", "Blue"]
            winner = random.choice(contestants)
            
            region.controller = winner
            
            print(f"    🏆 {winner} gains control")
            await asyncio.sleep(1)  # Brief pause for effect
    
    async def demo_tech_development(self):
        """Show technology development effects."""
        print("🔬 Technology development creates advantages but also friction:")
        print()
        
        for name, bloc in self.game.powers.items():
            if bloc.tech_level > 0:
                bonus = bloc.tech_bonus()
                drag = bloc.effective_drag()
                print(f"  {name}:")
                print(f"    🔬 Tech Level: {bloc.tech_level} (Bonus: +{bonus})")
                print(f"    📋 Regulatory Drag: {bloc.regulatory_drag}")
                print(f"    🤝 Trust Score: {bloc.trust_score}")
                print(f"    ⚖️ Effective Drag: {drag}")
                print()
    
    async def demo_military_buildup(self):
        """Show military competition effects."""
        print("⚔️ Military buildups affect regional stability:")
        print()
        
        total_military = sum(bloc.military_posture for bloc in self.game.powers.values())
        
        for name, bloc in self.game.powers.items():
            military_share = (bloc.military_posture / max(total_military, 1)) * 100
            print(f"  {name}: {bloc.military_posture}/5 ({military_share:.1f}% of total)")
        
        print(f"\n🌍 Total global military tension: {total_military}/15")
        
        if total_military > 10:
            print("⚠️ High military tension may trigger crisis events!")
        elif total_military < 5:
            print("🕊️ Low military tension promotes stability")
        else:
            print("⚖️ Moderate military tension - balanced deterrence")
    
    async def demo_final_scoring(self):
        """Show final victory point calculation."""
        print("🏆 Victory Point Calculation:")
        print()
        
        scores = []
        for name, bloc in self.game.powers.items():
            vp = bloc.bloc_vp()
            scores.append((name, vp))
            
            print(f"  {name}: {vp} Victory Points")
            print(f"    💰 GDP Tokens: {bloc.gdp_tokens}")
            print(f"    🔬 Tech Bonus: {bloc.tech_bonus()}")
            print(f"    ⚔️ Military: {bloc.military_posture * 2}")
            print(f"    🎭 Culture: {bloc.cultural_influence}")
            print(f"    🤝 Cohesion: {bloc.cohesion}")
            print(f"    🌍 Satellites: {len(bloc.satellites) * 3}")
            print(f"    🤝 Alliances: {len(bloc.alliances) * 2}")
            print(f"    📋 Drag Penalty: -{bloc.effective_drag()}")
            print()
        
        # Determine winner
        scores.sort(key=lambda x: x[1], reverse=True)
        winner_name, winner_score = scores[0]
        
        print(f"🥇 WINNER: {winner_name} with {winner_score} Victory Points!")
        
        if len(scores) > 1:
            margin = winner_score - scores[1][1]
            print(f"   Victory margin: {margin} points")
    
    async def update_visualization(self):
        """Update the web visualization with current game state."""
        # Broadcast current state to all connected clients
        state = self.bridge.serialize_game_state()
        await self.bridge.broadcast_update('full_state', state)
    
    async def wait_for_user(self):
        """Wait for user input to continue."""
        print("👆 Press Enter to continue (or Ctrl+C to exit)...")
        
        # In an async context, we need to handle input differently
        # For demo purposes, just wait a few seconds
        await asyncio.sleep(3)

def main():
    """Main entry point for the demo."""
    print("🎮 Conviction 2040 - Web Visualization Demo")
    print()
    
    # Check if required files exist
    required_files = ['conviction_abstract_map.html', 'models.py', 'conviction.py']
    missing_files = []
    
    for file in required_files:
        try:
            with open(file, 'r'):
                pass
        except FileNotFoundError:
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all game files are present before running the demo.")
        return
    
    print("✅ All required files found")
    print()
    
    # Run the demo
    demo = ConvictionDemo()
    
    try:
        asyncio.run(demo.start_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

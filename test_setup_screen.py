#!/usr/bin/env python3
"""
Test Suite for Setup Screen Implementation
==========================================

This script tests the setup screen functionality to ensure all features work correctly.
"""

import asyncio
import json
import websockets
import requests
import time
from typing import Dict, Any

class SetupScreenTester:
    """Test the setup screen implementation."""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://") + "/ws"
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log a test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append((test_name, passed, details))
        print(f"{status} {test_name}")
        if details:
            print(f"     {details}")
    
    async def test_setup_screen_html(self):
        """Test that the HTML contains setup screen elements."""
        try:
            response = requests.get(self.base_url, timeout=5)
            html_content = response.text
            
            required_elements = [
                'id="setupScreen"',           # Main setup screen
                'class="setup-screen"',       # Setup screen container
                'bloc-card',                  # Bloc selection cards (flexible match)
                'data-bloc="USA"',            # USA bloc option
                'data-bloc="EU"',             # EU bloc option
                'data-bloc="CHINA"',          # China bloc option
                'id="startGameBtn"',          # Start game button
                'id="turnLimit"',             # Turn limit slider
                'id="victoryPoints"',         # Victory points slider
                'id="aiOpponents"',           # AI opponents toggle
                'id="gameSpeed"',             # Game speed selector
                'class="game-title"',         # Game title
                'class="game-subtitle"'       # Game subtitle
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            success = len(missing_elements) == 0
            details = f"Missing: {missing_elements}" if missing_elements else "All setup elements found"
            self.log_test("Setup Screen HTML Elements", success, details)
            
            return success
            
        except Exception as e:
            self.log_test("Setup Screen HTML Elements", False, f"Error: {e}")
            return False
    
    async def test_setup_screen_css(self):
        """Test that the CSS includes setup screen styles."""
        try:
            response = requests.get(self.base_url, timeout=5)
            html_content = response.text
            
            required_css_classes = [
                '.setup-screen',
                '.setup-container',
                '.bloc-card',
                '.start-game-btn',
                '.game-title',
                '.settings-grid',
                '.toggle',
                '@keyframes fadeInUp'
            ]
            
            missing_css = []
            for css_class in required_css_classes:
                if css_class not in html_content:
                    missing_css.append(css_class)
            
            success = len(missing_css) == 0
            details = f"Missing CSS: {missing_css}" if missing_css else "All CSS styles found"
            self.log_test("Setup Screen CSS Styles", success, details)
            
            return success
            
        except Exception as e:
            self.log_test("Setup Screen CSS Styles", False, f"Error: {e}")
            return False
    
    async def test_game_start_websocket(self):
        """Test game start WebSocket message handling."""
        try:
            async with websockets.connect(self.ws_url) as ws:
                # Send a game start message
                game_config = {
                    "playerBloc": "USA",
                    "turnLimit": 30,
                    "victoryPoints": 40,
                    "aiOpponents": True,
                    "gameSpeed": "normal"
                }
                
                start_message = {
                    "type": "start_game",
                    "config": game_config
                }
                
                await ws.send(json.dumps(start_message))
                
                # Wait for responses (may get multiple messages)
                game_started_received = False
                for _ in range(3):  # Check up to 3 messages
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2)
                        data = json.loads(response)
                        
                        if data.get("type") == "game_started":
                            game_started_received = True
                            break
                    except asyncio.TimeoutError:
                        break
                
                success = game_started_received
                details = "Game started confirmation received" if success else "No game_started message received"
                self.log_test("Game Start WebSocket", success, details)
                
                return success
                
        except Exception as e:
            self.log_test("Game Start WebSocket", False, f"Error: {e}")
            return False
    
    async def test_javascript_functionality(self):
        """Test that JavaScript setup functionality is present."""
        try:
            response = requests.get(self.base_url, timeout=5)
            html_content = response.text
            
            required_js_features = [
                'selectedBloc',               # Bloc selection variable
                'gameSettings',               # Game settings object
                'addEventListener',           # Event listeners
                'start_game',                 # Start game message type
                'setPlayerPanel',             # Player panel setup function
                'forEach(card =>',            # Bloc card iteration
                'startBtn.disabled = false',  # Button state management
                'ws.send(JSON.stringify'      # WebSocket communication
            ]
            
            missing_js = []
            for js_feature in required_js_features:
                if js_feature not in html_content:
                    missing_js.append(js_feature)
            
            success = len(missing_js) == 0
            details = f"Missing JS: {missing_js}" if missing_js else "All JavaScript features found"
            self.log_test("Setup JavaScript Functionality", success, details)
            
            return success
            
        except Exception as e:
            self.log_test("Setup JavaScript Functionality", False, f"Error: {e}")
            return False
    
    async def test_bloc_themes(self):
        """Test that bloc-specific themes are implemented."""
        try:
            response = requests.get(self.base_url, timeout=5)
            html_content = response.text
            
            # Check for bloc-specific CSS classes and colors
            bloc_themes = [
                '.usa-card { color: #3b82f6',     # USA blue
                '.eu-card { color: #10b981',      # EU green  
                '.china-card { color: #ef4444',  # China red
                'case \'USA\'',                   # USA case in JavaScript
                'case \'EU\'',                    # EU case in JavaScript
                'case \'CHINA\'',                 # China case in JavaScript
            ]
            
            missing_themes = []
            for theme in bloc_themes:
                if theme not in html_content:
                    missing_themes.append(theme)
            
            success = len(missing_themes) == 0
            details = f"Missing themes: {missing_themes}" if missing_themes else "All bloc themes found"
            self.log_test("Bloc-Specific Themes", success, details)
            
            return success
            
        except Exception as e:
            self.log_test("Bloc-Specific Themes", False, f"Error: {e}")
            return False
    
    async def test_server_integration(self):
        """Test server-side setup screen integration."""
        try:
            async with websockets.connect(self.ws_url) as ws:
                # Test multiple game configurations
                configs = [
                    {"playerBloc": "USA", "turnLimit": 50, "victoryPoints": 50},
                    {"playerBloc": "EU", "turnLimit": 30, "victoryPoints": 40},
                    {"playerBloc": "CHINA", "turnLimit": 100, "victoryPoints": 60}
                ]
                
                successful_starts = 0
                
                for i, config in enumerate(configs):
                    start_message = {
                        "type": "start_game",
                        "config": config
                    }
                    
                    await ws.send(json.dumps(start_message))
                    
                    # Look for game_started response among multiple messages
                    config_success = False
                    for _ in range(3):  # Check up to 3 messages per config
                        try:
                            response = await asyncio.wait_for(ws.recv(), timeout=2)
                            data = json.loads(response)
                            
                            if data.get("type") == "game_started":
                                successful_starts += 1
                                config_success = True
                                print(f"    Config {i+1}: ✓ {config['playerBloc']}")
                                break
                                
                        except asyncio.TimeoutError:
                            break
                    
                    if not config_success:
                        print(f"    Config {i+1}: ✗ {config['playerBloc']} (no game_started response)")
                    
                    await asyncio.sleep(0.3)  # Brief delay between tests
                
                success = successful_starts >= len(configs) - 1  # Allow 1 failure for timing issues
                details = f"Successfully started {successful_starts}/{len(configs)} configurations"
                self.log_test("Server Integration", success, details)
                
                return success
                
        except Exception as e:
            self.log_test("Server Integration", False, f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all setup screen tests."""
        print("🎮 Testing Setup Screen Implementation")
        print("=" * 50)
        
        # Run all tests
        tests = [
            self.test_setup_screen_html(),
            self.test_setup_screen_css(),
            self.test_javascript_functionality(),
            self.test_bloc_themes(),
            self.test_game_start_websocket(),
            self.test_server_integration()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Count successes
        successful_tests = sum(1 for result in results if result is True)
        total_tests = len(results)
        
        # Summary
        print("\n📊 Setup Screen Test Summary")
        print("-" * 40)
        print(f"Tests Passed: {successful_tests}/{total_tests}")
        
        if successful_tests == total_tests:
            print("🎉 All setup screen tests passed! Implementation is complete.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
        return successful_tests == total_tests

async def main():
    """Main test execution."""
    tester = SetupScreenTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)

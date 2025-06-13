#!/usr/bin/env python3
"""
Test Suite for Sidebar Player Panel
===================================

This script tests the sidebar implementation to ensure all features work correctly.
"""

import asyncio
import json
import websockets
import requests
import time
from typing import Dict, Any

class SidebarTester:
    """Test the sidebar player panel functionality."""
    
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
    
    async def test_server_running(self):
        """Test if the server is running and accessible."""
        try:
            response = requests.get(self.base_url, timeout=5)
            self.log_test("Server Running", response.status_code == 200)
            return True
        except Exception as e:
            self.log_test("Server Running", False, f"Error: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection establishment."""
        try:
            async with websockets.connect(self.ws_url) as ws:
                self.log_test("WebSocket Connection", True)
                return ws
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Error: {e}")
            return None
    
    async def test_player_bloc_assignment(self):
        """Test player bloc assignment functionality."""
        assignments = []
        
        for i in range(3):  # Test 3 connections for USA, EU, China
            try:
                # Add a small delay to ensure distinct connections
                if i > 0:
                    await asyncio.sleep(0.1)
                    
                async with websockets.connect(self.ws_url) as ws:
                    # Send bloc assignment request
                    await ws.send(json.dumps({"type": "get_player_bloc"}))
                    
                    # Wait for multiple messages - first might be game state
                    messages_received = 0
                    while messages_received < 3:  # Try to get up to 3 messages
                        try:
                            response = await asyncio.wait_for(ws.recv(), timeout=2)
                            data = json.loads(response)
                            messages_received += 1
                            
                            print(f"  Connection {i+1} message {messages_received}: {data.get('type', 'unknown')}")
                            
                            if data.get("type") == "player_bloc":
                                assignments.append(data.get("bloc"))
                                print(f"    → Assigned to: {data.get('bloc')}")
                                break
                        except asyncio.TimeoutError:
                            break  # No more messages
                    
                    await asyncio.sleep(0.2)  # Longer delay to ensure connection cleanup
            except Exception as e:
                self.log_test(f"Player Assignment {i+1}", False, f"Error: {e}")
                return
        
        expected_blocs = set(["USA", "EU", "China"])
        received_blocs = set(assignments)
        success = received_blocs == expected_blocs and len(assignments) == 3
        
        self.log_test("Player Bloc Assignment", success, 
                     f"Got: {assignments}, Contains all blocs: {received_blocs == expected_blocs}")
    
    async def test_turn_submission(self):
        """Test turn submission functionality."""
        try:
            async with websockets.connect(self.ws_url) as ws:
                # Get player assignment first
                await ws.send(json.dumps({"type": "get_player_bloc"}))
                
                # Wait for messages and find the player_bloc response
                assignment_data = None
                messages_received = 0
                while messages_received < 3:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=3)
                        data = json.loads(response)
                        messages_received += 1
                        
                        if data.get("type") == "player_bloc":
                            assignment_data = data
                            break
                    except asyncio.TimeoutError:
                        break
                
                if not assignment_data or assignment_data.get("type") != "player_bloc":
                    self.log_test("Turn Submission Setup", False, f"No bloc assignment: {assignment_data}")
                    return
                
                player_bloc = assignment_data.get("bloc")
                print(f"  Testing turn submission for bloc: {player_bloc}")
                
                # Submit a test turn
                turn_data = {
                    "action": "submit_turn",
                    "bloc": player_bloc,
                    "budget": {
                        "military": 20,
                        "tech": 15,
                        "culture": 10,
                        "infra": 25,
                        "diplomacy": 30
                    },
                    "card": "Economic Development"
                }
                
                await ws.send(json.dumps(turn_data))
                
                # Wait for confirmation
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                confirmation = json.loads(response)
                
                success = (confirmation.get("type") == "turn_submitted" and 
                          confirmation.get("accepted") is True)
                self.log_test("Turn Submission", success, 
                             f"Bloc: {player_bloc}, Confirmation: {confirmation}")
                
        except Exception as e:
            self.log_test("Turn Submission", False, f"Error: {e}")
    
    async def test_html_content(self):
        """Test that the HTML contains required sidebar elements."""
        try:
            response = requests.get(self.base_url, timeout=5)
            html_content = response.text
            
            required_elements = [
                'id="playerPanel"',           # Main sidebar panel
                'class="panel-header"',       # Draggable header
                'minimize-btn',               # Minimize button (part of class)
                'close-btn',                  # Close button (part of class)
                'id="militarySlider"',        # Budget sliders
                'id="actionCard"',            # Action card selector
                'id="submitTurn"'             # Submit button
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            success = len(missing_elements) == 0
            details = f"Missing: {missing_elements}" if missing_elements else "All elements found"
            self.log_test("HTML Sidebar Elements", success, details)
            
        except Exception as e:
            self.log_test("HTML Sidebar Elements", False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Testing Sidebar Player Panel Implementation")
        print("=" * 50)
        
        # Test server availability
        if not await self.test_server_running():
            print("⚠️  Server not running. Please start with: python web_bridge.py")
            return
        
        # Run all tests
        await self.test_html_content()
        await self.test_websocket_connection()
        await self.test_player_bloc_assignment()
        await self.test_turn_submission()
        
        # Summary
        print("\n📊 Test Summary")
        print("-" * 30)
        passed = sum(1 for _, result, _ in self.test_results if result)
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Sidebar implementation is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
        return passed == total

async def main():
    """Main test execution."""
    tester = SidebarTester()
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

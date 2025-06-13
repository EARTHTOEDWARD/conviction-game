# test_web_visualization.py - Test script to verify web visualization setup
"""
Simple test to verify that the Conviction web visualization system is working correctly.
"""

import asyncio
import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import aiohttp
        print("  ✅ aiohttp imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import aiohttp: {e}")
        return False
    
    try:
        import aiohttp_cors
        print("  ✅ aiohttp_cors imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import aiohttp_cors: {e}")
        return False
    
    try:
        from models import Bloc, ProxyRegion
        print("  ✅ models imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import models: {e}")
        return False
    
    try:
        from conviction import ConvictionGame
        print("  ✅ conviction imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import conviction: {e}")
        return False
    
    try:
        from web_bridge import ConvictionWebBridge
        print("  ✅ web_bridge imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import web_bridge: {e}")
        return False
    
    return True

def test_file_existence():
    """Test that all required files exist."""
    print("\n📁 Testing file existence...")
    
    required_files = [
        'conviction_abstract_map.html',
        'models.py',
        'conviction.py',
        'web_bridge.py',
        'quickstart_demo.py',
        'requirements.txt'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} exists")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    return all_exist

def test_game_creation():
    """Test that the game can be created and initialized."""
    print("\n🎮 Testing game creation...")
    
    try:
        from conviction import ConvictionGame
        game = ConvictionGame()
        game.create_simple_map()
        print("  ✅ ConvictionGame created and initialized")
        
        # Test basic game properties
        assert hasattr(game, 'powers'), "Game should have powers attribute"
        assert len(game.powers) == 2, "Game should have 2 powers"
        assert 'Red' in game.powers, "Game should have Red power"
        assert 'Blue' in game.powers, "Game should have Blue power"
        print("  ✅ Game has correct structure")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to create game: {e}")
        return False

def test_web_bridge_creation():
    """Test that the web bridge can be created."""
    print("\n🌐 Testing web bridge creation...")
    
    try:
        from conviction import ConvictionGame
        from web_bridge import ConvictionWebBridge
        
        game = ConvictionGame()
        game.create_simple_map()
        
        bridge = ConvictionWebBridge(game)
        print("  ✅ ConvictionWebBridge created successfully")
        
        # Test serialization
        state = bridge.serialize_game_state()
        assert 'regions' in state, "State should contain regions"
        assert 'blocs' in state, "State should contain blocs"
        print("  ✅ Game state serialization works")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to create web bridge: {e}")
        return False

async def test_server_startup():
    """Test that the server can start (but don't leave it running)."""
    print("\n🚀 Testing server startup...")
    
    try:
        from conviction import ConvictionGame
        from web_bridge import ConvictionWebBridge
        
        game = ConvictionGame()
        game.create_simple_map()
        
        bridge = ConvictionWebBridge(game)
        
        # Start server on different port to avoid conflicts
        runner = await bridge.run(host='localhost', port=8081)
        print("  ✅ Server started successfully on port 8081")
        
        # Clean up
        await runner.cleanup()
        print("  ✅ Server stopped successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        return False

def test_html_file():
    """Test that the HTML visualization file is valid."""
    print("\n🎨 Testing HTML visualization file...")
    
    try:
        with open('conviction_abstract_map.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic HTML structure checks
        assert '<!DOCTYPE html>' in content, "HTML should have DOCTYPE"
        assert '<html' in content, "HTML should have html tag"
        assert '<canvas' in content, "HTML should have canvas element"
        assert 'CONVICTION' in content, "HTML should contain game title"
        assert 'WebSocket' in content, "HTML should have WebSocket code"
        
        print("  ✅ HTML file has correct structure")
        print(f"  ✅ HTML file size: {len(content):,} characters")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to validate HTML file: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    print("🎯 CONVICTION WEB VISUALIZATION - INSTALLATION TEST")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("File Existence Test", test_file_existence),
        ("Game Creation Test", test_game_creation),
        ("Web Bridge Test", test_web_bridge_creation),
        ("HTML Validation Test", test_html_file),
        ("Server Startup Test", test_server_startup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your Conviction web visualization is ready to use!")
        print("\nTo start the demo, run:")
        print("  python quickstart_demo.py")
    else:
        print(f"\n⚠️ {total-passed} tests failed.")
        print("Please check the error messages above and fix any issues.")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)

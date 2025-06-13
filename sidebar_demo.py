#!/usr/bin/env python3
"""
Sidebar Player Panel Demo
========================

This demo showcases the new sidebar player control panel implementation.

Features demonstrated:
- Player bloc assignment (USA, EU, China)
- Draggable sidebar panel
- Minimize/maximize functionality
- Close/restore panel with floating button
- Budget allocation sliders
- Action card selection
- Turn submission and validation
- Real-time WebSocket communication

Usage:
    python sidebar_demo.py

Then open multiple browser tabs to http://localhost:8080 to see different
players assigned to different blocs with their respective themed panels.
"""

import asyncio
import logging
from web_bridge import ConvictionWebBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_sidebar_demo():
    """Run the sidebar player panel demo."""
    print("=" * 60)
    print("🎮 CONVICTION GAME - SIDEBAR PLAYER PANEL DEMO")
    print("=" * 60)
    print()
    print("✨ Features:")
    print("  • Dynamic player bloc assignment (USA/EU/China)")
    print("  • Draggable sidebar panels with bloc-specific themes")
    print("  • Minimize/maximize and close/restore functionality")
    print("  • Budget allocation sliders with real-time feedback")
    print("  • Action card selection and turn submission")
    print("  • WebSocket-based real-time communication")
    print()
    print("🚀 Starting server...")
    
    # Create and start the web bridge
    bridge = ConvictionWebBridge()
    
    print(f"🌐 Server running at: http://localhost:8080")
    print()
    print("📋 Instructions:")
    print("  1. Open http://localhost:8080 in your browser")
    print("  2. Open multiple tabs to see different player assignments")
    print("  3. Test the drag-and-drop functionality")
    print("  4. Try minimize/maximize and close/restore")
    print("  5. Adjust budget sliders and submit turns")
    print()
    print("🎯 Player Assignment:")
    print("  • First connection  → USA (Blue theme)")
    print("  • Second connection → EU (Green theme)")
    print("  • Third connection  → China (Red theme)")
    print("  • Pattern repeats for additional connections")
    print()
    print("Press Ctrl+C to stop the demo")
    print("-" * 60)
    
    try:
        await bridge.run()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_sidebar_demo())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

# Conviction Game - Web Visualization Guide

## 🎯 Quick Start

Your Conviction game now has a beautiful web-based visualization! Here's how to use it:

### 1. Run the Demo
```bash
python quickstart_demo.py
```

This will:
- Start a web server on `http://localhost:8080`
- Open your browser automatically
- Run through an interactive demo showing all game features

### 2. View the Visualization

The web page shows:
- **Abstract world map** with artistic continental shapes
- **Power blocs** as large colored circles (USA=Blue, EU=Green, China=Red)
- **Influence regions** as smaller circles with dice indicators
- **Real-time updates** as the game progresses

### 3. Features

#### Visual Elements
- 🌍 **World Map**: Abstract artistic representation of global regions
- 🔵 **Major Powers**: Large circles representing USA, EU, China
- ⚂ **Influence Dice**: Shows control level in each region
- 🔗 **Strategic Connections**: Lines showing relationships between regions

#### Real-Time Updates
- Budget allocation effects
- Region control changes
- Technology development
- Military buildups
- Victory point calculations

## 🛠️ Files Created

| File | Purpose |
|------|---------|
| `conviction_abstract_map.html` | Main web visualization |
| `web_bridge.py` | WebSocket server for real-time updates |
| `quickstart_demo.py` | Interactive demo |
| `requirements.txt` | Python dependencies |
| `test_web_visualization.py` | Installation test |

## 🔧 Technical Details

### Architecture
- **Frontend**: HTML5 Canvas with real-time graphics
- **Backend**: Python aiohttp WebSocket server
- **Communication**: JSON messages over WebSocket
- **Integration**: Works with existing Conviction game logic

### API Endpoints
- `GET /` - Serve the map visualization
- `GET /ws` - WebSocket for real-time updates
- `GET /api/state` - Get current game state
- `POST /api/action` - Submit game actions

### WebSocket Messages
```json
{
  "type": "full_state",
  "data": {
    "turn": 1,
    "phase": "Planning",
    "regions": [...],
    "blocs": [...]
  }
}
```

## 🎮 Using with Your Game

### Basic Integration
```python
from conviction import ConvictionGame
from web_bridge import ConvictionWebBridge

# Create game
game = ConvictionGame()
game.create_simple_map()

# Start web visualization
bridge = ConvictionWebBridge(game)
await bridge.run()
```

### Real-Time Updates
```python
# Notify of region changes
await bridge.notify_region_change("North Atlantic", "USA", 2)

# Notify of phase changes
await bridge.notify_phase_change(2, "Resolution")

# Full state update
await bridge.broadcast_update('full_state', game_state)
```

## 🎨 Customization

### Visual Styling
Edit `conviction_abstract_map.html`:
- Colors in the CSS section
- Region positions in the JavaScript
- Visual effects and animations

### Game Integration
Edit `web_bridge.py`:
- Add new message types
- Modify state serialization
- Add custom game actions

## 🚨 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill existing servers
pkill -f quickstart_demo.py
# Or use a different port
python -c "from web_bridge import run_standalone_server; import asyncio; asyncio.run(run_standalone_server())"
```

**Module import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**WebSocket connection failed:**
- Check firewall settings
- Ensure nothing else is using port 8080
- Try refreshing the browser page

### Testing
```bash
# Run full test suite
python test_web_visualization.py
```

## 🎯 Next Steps

1. **Explore the Demo**: Run `quickstart_demo.py` and watch the visualization
2. **Integrate with Real Game**: Use `ConvictionWebBridge` in your game loops
3. **Customize Visuals**: Modify the HTML/CSS to match your preferences
4. **Add Features**: Extend the WebSocket API for new game mechanics

## 🎉 Congratulations!

You now have a modern, interactive web visualization for your Conviction game! The system provides:

- ✅ Real-time visual feedback
- ✅ Professional game board appearance  
- ✅ Easy integration with existing code
- ✅ Extensible architecture for future features

Happy gaming! 🎮

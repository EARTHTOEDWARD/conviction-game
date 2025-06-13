# web_bridge.py - WebSocket bridge for real-time Conviction game visualization
import asyncio
import json
import logging
from typing import Dict, List, Optional
from aiohttp import web, WSMsgType
import aiohttp_cors
from models import Bloc, ProxyRegion
from conviction import ConvictionGame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConvictionWebBridge:
    """WebSocket bridge that connects the Conviction game to the web visualization."""
    
    def __init__(self, game: Optional['ConvictionGame'] = None):
        self.game = game
        self.websockets: List[web.WebSocketResponse] = []
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Set up HTTP and WebSocket routes."""
        # Serve the HTML map file
        self.app.router.add_get('/', self.serve_map)
        self.app.router.add_get('/map', self.serve_map)
        
        # WebSocket endpoint for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # API endpoints for game state
        self.app.router.add_get('/api/state', self.get_game_state)
        self.app.router.add_post('/api/action', self.handle_action)
        
        # Enable CORS for all routes
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def serve_map(self, request):
        """Serve the HTML map visualization."""
        try:
            with open('conviction_abstract_map.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text="Map file not found", status=404)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.append(ws)
        logger.info(f"New WebSocket connection. Total: {len(self.websockets)}")
        
        # Send initial game state
        if self.game:
            await self.send_game_state(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON received: {msg.data}")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            if ws in self.websockets:
                self.websockets.remove(ws)
            logger.info(f"WebSocket disconnected. Total: {len(self.websockets)}")
        
        return ws
    
    async def handle_websocket_message(self, ws: web.WebSocketResponse, data: Dict):
        """Handle incoming WebSocket messages."""
        message_type = data.get('type')
        
        if message_type == 'get_state':
            await self.send_game_state(ws)
        elif message_type == 'action' and self.game:
            # Handle game actions
            action_data = data.get('data', {})
            await self.process_game_action(action_data)
        elif data.get('action') == 'submit_turn':
            # Handle player turn submissions
            await self.handle_player_action(ws, data)
    
    async def handle_player_action(self, ws: web.WebSocketResponse, data: Dict):
        """Handle actions from players."""
        action = data.get('action')
        
        if action == 'submit_turn':
            bloc = data.get('bloc')
            budget = data.get('budget')
            card = data.get('card')
            
            logger.info(f"\n{bloc} submitted turn:")
            logger.info(f"  Budget: {budget}")
            logger.info(f"  Card: {card}")
            
            # Store the submission (in a real game, validate and process)
            if not hasattr(self, 'turn_submissions'):
                self.turn_submissions = {}
            
            self.turn_submissions[bloc] = {
                'budget': budget,
                'card': card,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # Send confirmation
            await ws.send_str(json.dumps({
                'type': 'turn_submitted',
                'bloc': bloc,
                'accepted': True
            }))
            
            # Check if all players submitted
            if len(self.turn_submissions) == 3:
                logger.info("\nAll players have submitted!")
                await self.process_turn()
    
    async def process_turn(self):
        """Process the turn once all players have submitted."""
        # This is where you'd integrate with your game engine
        logger.info("\nProcessing turn...")
        
        # For demo: simulate some results
        await asyncio.sleep(2)
        
        # Clear submissions for next turn
        self.turn_submissions = {}
        
        # Broadcast phase change
        await self.broadcast_update('phase_update', {
            'turn': getattr(self.game, 'turn', 1),
            'phase': 'Resolution'
        })
        
        # After processing, return to planning phase
        await asyncio.sleep(3)
        await self.broadcast_update('phase_update', {
            'turn': getattr(self.game, 'turn', 1) + 1,
            'phase': 'Planning'
        })
    
    async def get_game_state(self, request):
        """HTTP endpoint to get current game state."""
        if not self.game:
            return web.json_response({'error': 'No game loaded'}, status=400)
        
        state = self.serialize_game_state()
        return web.json_response(state)
    
    async def handle_action(self, request):
        """HTTP endpoint to handle game actions."""
        if not self.game:
            return web.json_response({'error': 'No game loaded'}, status=400)
        
        try:
            data = await request.json()
            result = await self.process_game_action(data)
            return web.json_response({'success': True, 'result': result})
        except Exception as e:
            logger.error(f"Action handling error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    def serialize_game_state(self) -> Dict:
        """Convert game state to JSON-serializable format."""
        if not self.game:
            return {}
        
        # Convert regions (using provinces from the game)
        regions_data = []
        for region_name, region in self.game.provinces.items():
            regions_data.append({
                'name': region_name,
                'owner': region.controller or 'Neutral',
                'die': 3  # Default die value for visualization
            })
        
        # Convert blocs
        blocs_data = []
        for bloc in self.game.powers.values():
            blocs_data.append(bloc.to_dict())
        
        return {
            'turn': getattr(self.game, 'turn', 1),
            'phase': getattr(self.game, 'phase', 'Planning'),
            'regions': regions_data,
            'blocs': blocs_data,
            'game_over': getattr(self.game, 'game_over', False)
        }
    
    async def send_game_state(self, ws: web.WebSocketResponse):
        """Send current game state to a WebSocket client."""
        state = self.serialize_game_state()
        message = {
            'type': 'full_state',
            'data': state
        }
        
        try:
            await ws.send_str(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending game state: {e}")
    
    async def broadcast_update(self, update_type: str, data: Dict):
        """Broadcast an update to all connected WebSocket clients."""
        message = {
            'type': update_type,
            'data': data
        }
        
        # Remove disconnected websockets
        active_websockets = []
        for ws in self.websockets:
            if ws.closed:
                continue
            
            try:
                await ws.send_str(json.dumps(message))
                active_websockets.append(ws)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
        
        self.websockets = active_websockets
    
    async def process_game_action(self, action_data: Dict):
        """Process a game action and broadcast updates."""
        # This would integrate with your game logic
        # For now, just broadcast the action
        await self.broadcast_update('action_result', action_data)
        return "Action processed"
    
    async def notify_region_change(self, region_name: str, new_owner: str, die_value: int):
        """Notify clients of a region ownership change."""
        await self.broadcast_update('region_update', {
            'region': region_name,
            'owner': new_owner,
            'die': die_value
        })
    
    async def notify_phase_change(self, turn: int, phase: str):
        """Notify clients of a phase change."""
        await self.broadcast_update('phase_update', {
            'turn': turn,
            'phase': phase
        })
    
    def set_game(self, game: 'ConvictionGame'):
        """Set the game instance for the bridge."""
        self.game = game
    
    async def run(self, host='localhost', port=8080):
        """Start the web server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Conviction web bridge running on http://{host}:{port}")
        logger.info(f"Open http://{host}:{port} to view the game map")
        
        return runner

# Standalone server for testing
async def run_standalone_server():
    """Run the web bridge as a standalone server for testing."""
    bridge = ConvictionWebBridge()
    
    # Create a dummy game state for demonstration
    dummy_game = type('DummyGame', (), {})()
    dummy_game.turn = 1
    dummy_game.phase = 'Planning'
    dummy_game.game_over = False
    
    # Create some dummy regions (using province names from game)
    dummy_game.provinces = {
        "North": type('Province', (), {'name': 'North', 'controller': 'Red'}),
        "South": type('Province', (), {'name': 'South', 'controller': 'Blue'}),
        "East": type('Province', (), {'name': 'East', 'controller': None}),
        "West": type('Province', (), {'name': 'West', 'controller': None}),
    }
    
    # Create dummy blocs
    dummy_game.powers = {
        'Red': Bloc('Red'),
        'Blue': Bloc('Blue')
    }
    
    bridge.set_game(dummy_game)
    
    try:
        runner = await bridge.run()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(run_standalone_server())

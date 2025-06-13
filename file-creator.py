# create_conviction_files.py
"""
Helper script to create all the Conviction game files.
Run this in your conviction-game directory.
"""

import os

def create_file(filename, content):
    """Create a file with the given content."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {filename}")

# File contents
conviction_abstract_map_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conviction - Abstract World Map</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1a1a2e;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }

        #mapCanvas {
            background: #0f3460;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .title {
            position: absolute;
            top: 30px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 3em;
            font-weight: 200;
            letter-spacing: 0.2em;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <h1 class="title">CONVICTION 2040</h1>
    <canvas id="mapCanvas" width="1400" height="700"></canvas>

    <script>
        const canvas = document.getElementById('mapCanvas');
        const ctx = canvas.getContext('2d');

        // Ocean gradient
        const oceanGradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        oceanGradient.addColorStop(0, '#0f3460');
        oceanGradient.addColorStop(0.5, '#16213e');
        oceanGradient.addColorStop(1, '#0f3460');

        // Draw ocean background
        ctx.fillStyle = oceanGradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw abstract continents
        function drawContinent(path, color = 'rgba(94, 84, 142, 0.3)') {
            ctx.fillStyle = color;
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            
            ctx.beginPath();
            ctx.moveTo(path[0].x, path[0].y);
            
            // Create smooth curves through points
            for (let i = 1; i < path.length - 2; i++) {
                const xc = (path[i].x + path[i + 1].x) / 2;
                const yc = (path[i].y + path[i + 1].y) / 2;
                ctx.quadraticCurveTo(path[i].x, path[i].y, xc, yc);
            }
            
            // Connect last points
            ctx.quadraticCurveTo(path[path.length - 2].x, path[path.length - 2].y, path[path.length - 1].x, path[path.length - 1].y);
            ctx.closePath();
            
            ctx.fill();
            ctx.stroke();
        }

        // Simplified continent shapes
        const northAmerica = [
            {x: 150, y: 150}, {x: 280, y: 120}, {x: 350, y: 140},
            {x: 380, y: 200}, {x: 360, y: 280}, {x: 340, y: 350},
            {x: 300, y: 380}, {x: 250, y: 380}, {x: 200, y: 340},
            {x: 160, y: 280}, {x: 140, y: 220}, {x: 150, y: 150}
        ];

        const southAmerica = [
            {x: 320, y: 400}, {x: 340, y: 420}, {x: 360, y: 480},
            {x: 350, y: 540}, {x: 330, y: 580}, {x: 300, y: 600},
            {x: 280, y: 580}, {x: 270, y: 520}, {x: 280, y: 460},
            {x: 300, y: 420}, {x: 320, y: 400}
        ];

        const europe = [
            {x: 680, y: 120}, {x: 740, y: 110}, {x: 780, y: 130},
            {x: 800, y: 160}, {x: 790, y: 200}, {x: 760, y: 240},
            {x: 720, y: 260}, {x: 680, y: 250}, {x: 660, y: 220},
            {x: 650, y: 180}, {x: 660, y: 140}, {x: 680, y: 120}
        ];

        const africa = [
            {x: 700, y: 280}, {x: 740, y: 300}, {x: 780, y: 340},
            {x: 800, y: 400}, {x: 790, y: 460}, {x: 760, y: 500},
            {x: 720, y: 520}, {x: 680, y: 500}, {x: 660, y: 460},
            {x: 650, y: 400}, {x: 660, y: 340}, {x: 680, y: 300},
            {x: 700, y: 280}
        ];

        const asia = [
            {x: 820, y: 120}, {x: 980, y: 100}, {x: 1100, y: 140},
            {x: 1180, y: 200}, {x: 1200, y: 280}, {x: 1180, y: 360},
            {x: 1120, y: 400}, {x: 1040, y: 420}, {x: 960, y: 400},
            {x: 880, y: 360}, {x: 820, y: 300}, {x: 800, y: 240},
            {x: 810, y: 180}, {x: 820, y: 120}
        ];

        const oceania = [
            {x: 1050, y: 480}, {x: 1120, y: 500}, {x: 1160, y: 540},
            {x: 1140, y: 580}, {x: 1080, y: 590}, {x: 1020, y: 560},
            {x: 1010, y: 520}, {x: 1030, y: 490}, {x: 1050, y: 480}
        ];

        // Draw all continents
        drawContinent(northAmerica);
        drawContinent(southAmerica);
        drawContinent(europe);
        drawContinent(africa);
        drawContinent(asia);
        drawContinent(oceania);

        // Power bloc and influence region definitions
        const regions = [
            // Major Power Blocs (larger circles)
            {
                name: 'USA',
                x: 250, y: 250,
                radius: 80,
                color: '#3b82f6',
                isBloc: true
            },
            {
                name: 'EU',
                x: 720, y: 180,
                radius: 80,
                color: '#10b981',
                isBloc: true
            },
            {
                name: 'China',
                x: 1050, y: 320,
                radius: 80,
                color: '#ef4444',
                isBloc: true
            },
            
            // Influence Regions (smaller circles)
            {
                name: 'Arctic',
                x: 700, y: 60,
                radius: 30,
                color: '#94a3b8'
            },
            {
                name: 'N. Atlantic',
                x: 500, y: 180,
                radius: 40,
                color: '#94a3b8'
            },
            {
                name: 'Latin Am.',
                x: 300, y: 500,
                radius: 50,
                color: '#94a3b8'
            },
            {
                name: 'Africa',
                x: 720, y: 400,
                radius: 60,
                color: '#94a3b8'
            },
            {
                name: 'Mid East',
                x: 850, y: 280,
                radius: 50,
                color: '#94a3b8'
            },
            {
                name: 'Cent. Asia',
                x: 900, y: 200,
                radius: 45,
                color: '#94a3b8'
            },
            {
                name: 'S.E. Asia',
                x: 1100, y: 450,
                radius: 55,
                color: '#94a3b8'
            },
            {
                name: 'Pacific',
                x: 1200, y: 350,
                radius: 45,
                color: '#94a3b8'
            },
            {
                name: 'Indo-Pac',
                x: 950, y: 500,
                radius: 50,
                color: '#94a3b8'
            }
        ];

        // Draw influence connections
        function drawConnection(from, to, style = 'solid') {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 2;
            
            if (style === 'dotted') {
                ctx.setLineDash([8, 8]);
                ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)'; // Red for China
            } else {
                ctx.setLineDash([]);
            }
            
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();
            
            ctx.setLineDash([]); // Reset
        }

        // Draw specific connections
        const connections = [
            {from: 'USA', to: 'N. Atlantic'},
            {from: 'USA', to: 'Latin Am.'},
            {from: 'USA', to: 'Pacific'},
            {from: 'EU', to: 'N. Atlantic'},
            {from: 'EU', to: 'Arctic'},
            {from: 'EU', to: 'Africa'},
            {from: 'EU', to: 'Mid East'},
            {from: 'China', to: 'Cent. Asia'},
            {from: 'China', to: 'S.E. Asia'},
            {from: 'China', to: 'Pacific'},
            {from: 'China', to: 'Africa', style: 'dotted'}, // Special dotted line
            {from: 'Mid East', to: 'Cent. Asia'},
            {from: 'S.E. Asia', to: 'Indo-Pac'}
        ];

        // Draw all connections first (behind regions)
        connections.forEach(conn => {
            const from = regions.find(r => r.name === conn.from);
            const to = regions.find(r => r.name === conn.to);
            if (from && to) {
                drawConnection(from, to, conn.style);
            }
        });

        // Draw regions
        regions.forEach(region => {
            // Shadow for depth
            ctx.shadowBlur = 20;
            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
            
            // Outer glow for major blocs
            if (region.isBloc) {
                ctx.shadowBlur = 40;
                ctx.shadowColor = region.color;
            }
            
            // Circle fill
            ctx.fillStyle = region.color + (region.isBloc ? 'CC' : '66');
            ctx.beginPath();
            ctx.arc(region.x, region.y, region.radius, 0, Math.PI * 2);
            ctx.fill();
            
            // Circle border
            ctx.shadowBlur = 0;
            ctx.strokeStyle = region.isBloc ? '#fff' : region.color;
            ctx.lineWidth = region.isBloc ? 3 : 2;
            ctx.stroke();
            
            // Region name
            ctx.fillStyle = '#fff';
            ctx.font = region.isBloc ? 'bold 20px Inter' : '14px Inter';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(region.name, region.x, region.y);
            
            // Influence indicator (dice or dots)
            if (!region.isBloc) {
                ctx.font = '20px serif';
                ctx.fillText('⚂', region.x, region.y + 25);
            }
        });

        // Legend
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.font = '12px Inter';
        ctx.textAlign = 'left';
        
        const legendY = canvas.height - 50;
        ctx.fillText('Major Power Blocs', 50, legendY);
        ctx.fillText('Influence Regions', 200, legendY);
        ctx.fillText('Strategic Connections', 350, legendY);
        
        // Legend symbols
        ctx.fillStyle = '#3b82f6CC';
        ctx.beginPath();
        ctx.arc(60, legendY + 20, 10, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#94a3b866';
        ctx.beginPath();
        ctx.arc(210, legendY + 20, 8, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(340, legendY + 20);
        ctx.lineTo(380, legendY + 20);
        ctx.stroke();
        
        // Year indicator
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.font = '14px Inter';
        ctx.textAlign = 'right';
        ctx.fillText('Turn 1 • Planning Phase', canvas.width - 50, 50);
        
        // Store regions globally for updates
        window.gameRegions = regions;
        window.gameConnections = connections;
        
        // WebSocket connection for real-time updates
        let ws = null;
        let currentGameState = {
            turn: 1,
            phase: 'Planning',
            regions: {}
        };
        
        function connectWebSocket() {
            ws = new WebSocket('ws://localhost:8080/ws');
            
            ws.onopen = () => {
                console.log('Connected to Conviction game server');
                updateStatus('Connected', '#10b981');
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleGameUpdate(message);
            };
            
            ws.onclose = () => {
                console.log('Disconnected from server. Reconnecting...');
                updateStatus('Reconnecting...', '#f59e0b');
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                updateStatus('Connection Error', '#ef4444');
            };
        }
        
        function updateStatus(text, color) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(canvas.width - 200, 70, 150, 30);
            
            ctx.fillStyle = color;
            ctx.font = '12px Inter';
            ctx.textAlign = 'right';
            ctx.fillText(text, canvas.width - 60, 88);
        }
        
        function handleGameUpdate(message) {
            if (message.type === 'region_update') {
                updateRegion(message.data);
            } else if (message.type === 'phase_update') {
                updatePhase(message.data);
            } else if (message.regions) {
                // Full state update
                updateFullState(message);
            }
        }
        
        function updateRegion(data) {
            const region = regions.find(r => r.name === data.region);
            if (region && !region.isBloc) {
                // Update ownership color
                if (data.owner) {
                    const ownerColors = {
                        'USA': '#3b82f6',
                        'EU': '#10b981',
                        'China': '#ef4444',
                        'Neutral': '#94a3b8'
                    };
                    region.color = ownerColors[data.owner] || '#94a3b8';
                }
                
                // Store die value
                if (data.die !== null) {
                    region.die = data.die;
                }
                
                // Redraw the map
                redrawMap();
            }
        }
        
        function updatePhase(data) {
            currentGameState.turn = data.turn;
            currentGameState.phase = data.phase;
            redrawMap();
        }
        
        function updateFullState(state) {
            // Update all regions with game state
            state.regions.forEach(newRegion => {
                const region = regions.find(r => r.name === mapRegionName(newRegion.name));
                if (region && !region.isBloc) {
                    const ownerColors = {
                        'USA': '#3b82f6',
                        'EU': '#10b981',
                        'China': '#ef4444',
                        'Neutral': '#94a3b8'
                    };
                    region.color = ownerColors[newRegion.owner] || '#94a3b8';
                    region.die = newRegion.die || 3;
                    region.owner = newRegion.owner;
                }
            });
            
            if (state.turn) currentGameState.turn = state.turn;
            if (state.phase) currentGameState.phase = state.phase;
            
            redrawMap();
        }
        
        // Map full region names to abbreviated display names
        function mapRegionName(fullName) {
            const nameMap = {
                'Arctic Council': 'Arctic',
                'North Atlantic': 'N. Atlantic',
                'Latin America': 'Latin Am.',
                'Africa': 'Africa',
                'Middle East': 'Mid East',
                'Central Asia': 'Cent. Asia',
                'S.E. Asia': 'S.E. Asia',
                'Pacific Rim': 'Pacific',
                'Indo-Pacific': 'Indo-Pac'
            };
            return nameMap[fullName] || fullName;
        }
        
        function redrawMap() {
            // Clear canvas
            ctx.fillStyle = oceanGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Redraw continents
            drawContinent(northAmerica);
            drawContinent(southAmerica);
            drawContinent(europe);
            drawContinent(africa);
            drawContinent(asia);
            drawContinent(oceania);
            
            // Redraw connections
            connections.forEach(conn => {
                const from = regions.find(r => r.name === conn.from);
                const to = regions.find(r => r.name === conn.to);
                if (from && to) {
                    drawConnection(from, to, conn.style);
                }
            });
            
            // Redraw regions with updated colors
            regions.forEach(region => {
                // Shadow for depth
                ctx.shadowBlur = 20;
                ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                
                // Outer glow for major blocs
                if (region.isBloc) {
                    ctx.shadowBlur = 40;
                    ctx.shadowColor = region.color;
                }
                
                // Circle fill
                ctx.fillStyle = region.color + (region.isBloc ? 'CC' : '66');
                ctx.beginPath();
                ctx.arc(region.x, region.y, region.radius, 0, Math.PI * 2);
                ctx.fill();
                
                // Circle border
                ctx.shadowBlur = 0;
                ctx.strokeStyle = region.isBloc ? '#fff' : region.color;
                ctx.lineWidth = region.isBloc ? 3 : 2;
                ctx.stroke();
                
                // Region name
                ctx.fillStyle = '#fff';
                ctx.font = region.isBloc ? 'bold 20px Inter' : '14px Inter';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(region.name, region.x, region.y);
                
                // Influence indicator (dice)
                if (!region.isBloc && region.die) {
                    ctx.font = '20px serif';
                    const diceSymbols = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
                    ctx.fillText(diceSymbols[region.die] || '⚂', region.x, region.y + 25);
                }
            });
            
            // Redraw legend
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.font = '12px Inter';
            ctx.textAlign = 'left';
            
            const legendY = canvas.height - 50;
            ctx.fillText('Major Power Blocs', 50, legendY);
            ctx.fillText('Influence Regions', 200, legendY);
            ctx.fillText('Strategic Connections', 350, legendY);
            
            // Legend symbols
            ctx.fillStyle = '#3b82f6CC';
            ctx.beginPath();
            ctx.arc(60, legendY + 20, 10, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#94a3b866';
            ctx.beginPath();
            ctx.arc(210, legendY + 20, 8, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(340, legendY + 20);
            ctx.lineTo(380, legendY + 20);
            ctx.stroke();
            
            // Update turn/phase indicator
            ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.font = '14px Inter';
            ctx.textAlign = 'right';
            ctx.fillText(`Turn ${currentGameState.turn} • ${currentGameState.phase} Phase`, canvas.width - 50, 50);
        }
        
        // Add click handling for regions
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            regions.forEach(region => {
                const dx = x - region.x;
                const dy = y - region.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance <= region.radius) {
                    console.log('Clicked region:', region.name);
                    // Could add popup info or other interactions here
                }
            });
        });
        
        // Connect when page loads
        connectWebSocket();
    </script>
</body>
</html>'''

requirements_txt = '''# requirements.txt
# Core dependencies for Conviction game

# Web server and WebSocket support
aiohttp>=3.8.0
aiohttp-cors>=0.7.0

# For the terminal-based board render (optional)
rich>=13.0.0

# Async utilities
asyncio>=3.4.3

# Data handling
dataclasses>=0.6  # For Python 3.6 compatibility'''

# Main execution
if __name__ == "__main__":
    print("Creating Conviction game files...")
    print("-" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('models.py'):
        print("⚠️  Warning: models.py not found.")
        print("   Make sure you're running this in your conviction-game directory!")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            exit()
    
    # Create the files
    create_file('conviction_abstract_map.html', conviction_abstract_map_html)
    create_file('requirements.txt', requirements_txt)
    
    # Note: I'm not including the full Python files here to keep this script manageable
    # You'll need to copy those from the artifacts above
    
    print("\n" + "-" * 40)
    print("✅ Basic files created!")
    print("\nNext steps:")
    print("1. Copy web_bridge.py from the artifact above")
    print("2. Copy quickstart_demo.py from the artifact above")
    print("3. Run: pip install -r requirements.txt")
    print("4. Run: python quickstart_demo.py")
    print("\nEnjoy your game! 🎮")

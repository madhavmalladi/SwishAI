from flask import Flask, request, jsonify
from flask_cors import CORS
from app.player_data import generate_random_player, get_player_data, get_player_id

app = Flask(__name__)

# Comprehensive CORS setup
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"])

# Additional CORS headers for all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Handle preflight requests for all endpoints
@app.route('/api/<path:subpath>', methods=['OPTIONS'])
def handle_preflight(subpath):
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def get_bbref_image_url(full_name):
    """Generate Basketball Reference image URL from player name"""
    try:
        # Handle various name formats
        name_parts = full_name.lower().strip().split()
        
        if len(name_parts) < 2:
            return None
            
        first = name_parts[0]
        last = name_parts[-1]  # Use last part in case of multiple last names
        
        # Handle special cases and common variations
        if len(name_parts) > 2:
            # For names like "De'Aaron Fox" or "LaMelo Ball"
            if name_parts[1].startswith("'"):
                first = name_parts[0] + name_parts[1]
                last = name_parts[2] if len(name_parts) > 2 else name_parts[0]
            else:
                # For names like "Karl-Anthony Towns"
                last = name_parts[-1]
        
        # Remove apostrophes and other special characters from both first and last names
        first = ''.join(c for c in first if c.isalnum())
        last = ''.join(c for c in last if c.isalnum())
        
        # Generate BBRef ID
        player_id = f"{last[:5]}{first[:2]}01"
        return f"https://www.basketball-reference.com/req/202106291/images/players/{player_id}.jpg"
        
    except Exception as e:
        print(f"Error generating BBRef URL for {full_name}: {e}")
        return None

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello from backend"})

@app.route('/api/generate', methods=['GET'])
def generate_player():
    player = generate_random_player()
    if player:
        # Add Basketball Reference image URL to the player data
        player['image_url'] = get_bbref_image_url(player['name'])
        return jsonify(player)
    else:
        return jsonify({"error": "No players available"}), 500

@app.route('/api/player_image', methods=['GET'])
def get_player_image():
    name = request.args.get("name")
    if name:
        image_url = get_bbref_image_url(name)
        if image_url:
            return jsonify({"image_url": image_url})
        else:
            return jsonify({"error": "Could not generate image URL"}), 400
    else:
        return jsonify({"error": "Name parameter required"}), 400

@app.route('/api/player/<int:player_id>/image', methods=['GET'])
def get_player_image_endpoint(player_id):
    image_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
    return jsonify({"image_url": image_url})

@app.route("/api/get_stats", methods=['GET'])
def get_stats():
    player_id = get_player_id("Stephen Curry")
    stats = get_player_data(player_id)
    return jsonify(stats)

if __name__ == "__main__":
    app.run(port=5000, debug=True)

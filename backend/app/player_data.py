from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pandas as pd
import sqlite3
import os
import random
from collections import OrderedDict

# Database file paths
DB_PATH = "app/nba_players.db"
FILTERED_DB_PATH = "app/nba_players_filtered.db"

def get_players_from_db(db_path=None):
    """Load All-Star players from the database"""
    if db_path is None:
        # Use filtered database if it exists, otherwise use original
        db_path = FILTERED_DB_PATH if os.path.exists(FILTERED_DB_PATH) else DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if retirement_year column exists
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'retirement_year' in columns:
        cursor.execute("""
            SELECT id, name, all_star_count, retirement_year 
            FROM players 
            ORDER BY all_star_count DESC
        """)
        players_data = cursor.fetchall()
        # Convert to list of dictionaries
        return [{"id": player[0], "name": player[1], "all_star_count": player[2], "retirement_year": player[3]} for player in players_data]
    else:
        cursor.execute("SELECT id, name, all_star_count FROM players ORDER BY all_star_count DESC")
        players_data = cursor.fetchall()
        # Convert to list of dictionaries
        return [{"id": player[0], "name": player[1], "all_star_count": player[2]} for player in players_data]
    
    conn.close()

def database_exists_and_has_data(db_path=None):
    """Check if database exists and has All-Star data"""
    if db_path is None:
        # Check filtered database first, then original
        if os.path.exists(FILTERED_DB_PATH):
            db_path = FILTERED_DB_PATH
        else:
            db_path = DB_PATH
    
    if not os.path.exists(db_path):
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def get_player_data(player_id: int):
    """Get player career statistics from NBA API"""
    career = playercareerstats.PlayerCareerStats(player_id)
    df = career.get_data_frames()[0]

    seasons = df['SEASON_ID'].tolist()

    # Return as array of objects to maintain exact order
    stat_history = [
        {
            "stat": "PPG",
            "data": (seasons, (df['PTS'] / df['GP']).round(1).tolist())
        },
        {
            "stat": "APG", 
            "data": (seasons, (df['AST'] / df['GP']).round(1).tolist())
        },
        {
            "stat": "RPG",
            "data": (seasons, (df['REB'] / df['GP']).round(1).tolist())
        },
        {
            "stat": "SPG",
            "data": (seasons, (df['STL'] / df['GP']).round(1).tolist())
        },
        {
            "stat": "BPG",
            "data": (seasons, (df['BLK'] / df['GP']).round(1).tolist())
        },
        {
            "stat": "3PM",
            "data": (seasons, df['FG3M'].fillna(0).round(0).astype(int).tolist())
        }
    ]

    return stat_history

def get_player_pool(use_filtered=True):
    """Get the All-Star player pool from database"""
    if use_filtered and os.path.exists(FILTERED_DB_PATH):
        print("Loading filtered All-Star players from database...")
        player_pool = get_players_from_db(FILTERED_DB_PATH)
        print(f"Loaded {len(player_pool)} filtered All-Star players from database")
        return player_pool
    elif database_exists_and_has_data():
        print("Loading All-Star players from original database...")
        player_pool = get_players_from_db(DB_PATH)
        print(f"Loaded {len(player_pool)} All-Star players from database")
        return player_pool
    else:
        print("❌ No All-Star database found!")
        print("💡 Please run 'python scrape_allstars.py' first to create the database.")
        return []
    
def generate_random_player(use_filtered=True):
    """Generate a random All-Star player from the database"""
    player_pool = get_player_pool(use_filtered)
    
    if not player_pool:
        return None
    
    random_player = random.choice(player_pool)
    
    return {
        "id": random_player["id"],
        "name": random_player["name"],
        "all_star_count": random_player["all_star_count"]
    }

def get_player_id(full_name: str):
    matches = players.find_players_by_full_name(full_name)
    if not matches:
        raise ValueError(f"No player found with name '{full_name}'")
    return matches[0]['id']
    

if __name__ == "__main__":
    # Load All-Star players from database
    player_pool = get_player_pool()
    
    if player_pool:
        print(f"\n🎯 All-Star Player Pool Loaded Successfully!")
        df = pd.DataFrame(player_pool)
        print(f"\n📈 Database Summary:")
        print(f"  - Total players: {len(df)}")
        
        # Show retirement year info if available
        if 'retirement_year' in df.columns:
            active_players = df[df['retirement_year'].isna()].shape[0]
            retired_after_1980 = df[df['retirement_year'] >= 1980].shape[0]
            print(f"  - Active players: {active_players}")
            print(f"  - Retired after 1980: {retired_after_1980}")
    else:
        print("❌ Failed to load All-Star player pool")
import sqlite3
import json
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import time

# Database file path
DB_PATH = "app/nba_players.db"

def add_retirement_year_column():
    """Add retirement_year column to the database if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if retirement_year column exists
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'retirement_year' not in columns:
        cursor.execute("ALTER TABLE players ADD COLUMN retirement_year INTEGER")
        print("✅ Added retirement_year column to players table")
    
    conn.commit()
    conn.close()

def get_player_retirement_year(player_id):
    """Get the last year a player played in the NBA"""
    try:
        career = playercareerstats.PlayerCareerStats(player_id)
        df = career.get_data_frames()[0]
        
        if df.empty:
            return None
            
        # Get the last season year (convert from '2023-24' format to 2024)
        last_season = df['SEASON_ID'].iloc[-1]
        
        # Handle different season formats
        if isinstance(last_season, str):
            if '-' in last_season:
                # Format: '2023-24' -> 2024
                retirement_year = int(last_season.split('-')[1])
            else:
                # Format: '2024' -> 2024
                retirement_year = int(last_season)
        else:
            # Handle numeric format
            retirement_year = int(last_season)
        
        # Additional validation: check if this is a reasonable year
        current_year = 2024
        if retirement_year > current_year + 1:  # Allow for future seasons
            print(f"  Warning: Unrealistic retirement year {retirement_year} for player ID {player_id}")
            return None
            
        return retirement_year
        
    except Exception as e:
        print(f"Error getting retirement year for player ID {player_id}: {e}")
        return None

def update_retirement_years():
    """Update retirement years for all players in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all players
    cursor.execute("SELECT id, name FROM players")
    all_players = cursor.fetchall()
    
    print(f"Updating retirement years for {len(all_players)} players...")
    
    for i, (player_id, player_name) in enumerate(all_players):
        print(f"Processing {i+1}/{len(all_players)}: {player_name}")
        
        retirement_year = get_player_retirement_year(player_id)
        
        if retirement_year:
            cursor.execute("UPDATE players SET retirement_year = ? WHERE id = ?", 
                         (retirement_year, player_id))
            print(f"  {player_name}: Retired in {retirement_year}")
        else:
            print(f"  {player_name}: Could not determine retirement year")
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.2)
    
    conn.commit()
    conn.close()
    print("✅ Updated retirement years for all players")

def filter_players_by_retirement_year(min_retirement_year=1980):
    """Filter players to only include those who retired after the specified year"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get players who retired after the minimum year (or are still active)
    cursor.execute("""
        SELECT id, name, all_star_count, retirement_year 
        FROM players 
        WHERE retirement_year >= ? OR retirement_year IS NULL
        ORDER BY all_star_count DESC
    """, (min_retirement_year,))
    
    filtered_players = cursor.fetchall()
    
    print(f"Found {len(filtered_players)} players who retired after {min_retirement_year} or are still active")
    
    # Show some examples
    print("\nSample filtered players:")
    for i, (player_id, name, all_star_count, retirement_year) in enumerate(filtered_players[:10]):
        status = f"Retired {retirement_year}" if retirement_year else "Still Active"
        print(f"  {name}: {all_star_count} All-Stars, {status}")
    
    conn.close()
    return filtered_players

def create_filtered_database(filtered_players, output_db_path="app/nba_players_filtered.db"):
    """Create a new database with only the filtered players"""
    conn = sqlite3.connect(output_db_path)
    cursor = conn.cursor()
    
    # Create the same table structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            all_star_count INTEGER,
            retirement_year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert filtered players
    for player_id, name, all_star_count, retirement_year in filtered_players:
        cursor.execute("""
            INSERT INTO players (id, name, all_star_count, retirement_year) 
            VALUES (?, ?, ?, ?)
        """, (player_id, name, all_star_count, retirement_year))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created filtered database with {len(filtered_players)} players: {output_db_path}")

def main():
    print("🔄 Filtering NBA players by retirement year...")
    
    # Step 1: Add retirement_year column
    add_retirement_year_column()
    
    # Step 2: Update retirement years (this might take a while)
    print("\n⚠️  This step will take several minutes as it queries the NBA API for each player...")
    response = input("Do you want to continue? (y/n): ")
    if response.lower() != 'y':
        print("Exiting...")
        return
    
    update_retirement_years()
    
    # Step 3: Filter players
    filtered_players = filter_players_by_retirement_year(1980)
    
    # Step 4: Create new filtered database
    create_filtered_database(filtered_players)
    
    print("\n🎉 Database filtering complete!")
    print("You can now update your app to use the filtered database.")

if __name__ == "__main__":
    main() 
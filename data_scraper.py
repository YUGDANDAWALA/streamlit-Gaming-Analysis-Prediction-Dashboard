import pandas as pd
import mysql.connector
from typing import List, Optional
import requests
from sqlalchemy import create_engine

# ========== MySQL Configuration ==========
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # XAMPP default
}
DB_NAME = "esports_data"

# ========== Database Setup ==========
def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    tables = {
        "countries": """
            CREATE TABLE IF NOT EXISTS countries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            total_earnings BIGINT,
            num_players INT,
            top_game VARCHAR(100),
            game_earnings BIGINT,
            game_percent FLOAT
        )
        """,
        "players": """
            CREATE TABLE IF NOT EXISTS players (
            rank INT AUTO_INCREMENT PRIMARY KEY,
            player_id VARCHAR(100),
            player_name VARCHAR(100),
            total_earnings BIGINT,
            main_game VARCHAR(100),
            earnings_percent FLOAT
        )
        """,
        "tournaments": """
            CREATE TABLE IF NOT EXISTS tournaments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tournament_name VARCHAR(200),
            prize_pool BIGINT,
            game VARCHAR(100),
            participate_team INT,
            no_of_player INT
        )
        """,
        "teams": """
            CREATE TABLE IF NOT EXISTS teams (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_name VARCHAR(255),
            revenue INT,
            tournaments_played INT
        ) 
        """,
    }

    for table_name, table_sql in tables.items():
        cursor.execute(table_sql)

    conn.commit()
    cursor.close()
    conn.close()

# ========== Web Scraping ==========
def fetch_html_table(url):
    try:
        tables = pd.read_html(url)
        return tables[0] if tables else None
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def fetch_multiple_tables(urls: List[str]) -> Optional[pd.DataFrame]:
    frames = [fetch_html_table(url) for url in urls]
    frames = [df for df in frames if df is not None]
    return pd.concat(frames, ignore_index=True) if frames else None

# ========== Insert into MySQL ==========
def insert_into_mysql(df: pd.DataFrame, table: str, columns: List[str]):
    if df is None or df.empty:
        print(f"⚠️ No data for table `{table}`")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"USE {DB_NAME}")
    
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    try:
        data = df[columns].where(pd.notnull(df), None).values.tolist()
        cursor.executemany(query, data)
        conn.commit()
        print(f"✅ Inserted {cursor.rowcount} rows into `{table}`")
    except Exception as e:
        print(f"❌ Insert error in `{table}`: {e}")
    finally:
        cursor.close()
        conn.close()

def scrape_countries():
    print("\n🌍 Scraping Countries")
    url = "https://www.esportsearnings.com/countries"
    df = fetch_html_table(url)

    if df is not None:
        # Set proper column names
        df.columns = [
            "rank", "name", "total_earnings", "num_players", 
            "top_game", "game_earnings", "game_percent"
        ]

        # Clean and transform
        df["name"] = df["name"].astype(str)
        df["total_earnings"] = df["total_earnings"].replace(r'[\$,]', '', regex=True).astype(float)
        df["num_players"] = df["num_players"].astype(str).str.replace(r'[^\d]', '', regex=True).astype(int)
        df["top_game"] = df["top_game"].astype(str)
        df["game_earnings"] = df["game_earnings"].replace(r'[\$,]', '', regex=True).astype(float)
        df["game_percent"] = df["game_percent"].astype(str).str.replace('%', '').astype(float)

        # Final selection and deduplication
        df = df[["name", "total_earnings", "num_players", "top_game", "game_earnings", "game_percent"]]
        df = df.drop_duplicates()

        insert_into_mysql(df, "countries", ["name", "total_earnings", "num_players", "top_game", "game_earnings", "game_percent"])
    else:
        print("⚠️ No country data found.")

def scrape_players():
    print("\n👥 Scraping Players")
    urls = [f"https://www.esportsearnings.com/players/highest-earnings-top-{i}" if i else
            "https://www.esportsearnings.com/players/highest-earnings" for i in range(0, 1001, 100)]
    df = fetch_multiple_tables(urls)

    if df is not None:
        print(f"📊 Available columns in scraped 'players': {list(df.columns)}")

        # Drop the first unwanted column (encoding issue)
        if 'Â' in df.columns:
            df = df.drop(columns=['Â'])

        # Rename columns manually
        df.columns = [
            "player_id", "player_name", "total_earnings",
            "main_game", "game_earnings", "earnings_percent"
        ]

        # Clean and format
        df["player_id"] = df["player_id"].astype(str)
        df["player_name"] = df["player_name"].astype(str)
        df["total_earnings"] = df["total_earnings"].replace(r'[\$,]', '', regex=True).astype(float).astype(int)
        df["main_game"] = df["main_game"].astype(str)
        df["earnings_percent"] = df["earnings_percent"].astype(str).str.replace(r'%', '', regex=True).astype(float)

        # Final insert-ready dataframe and deduplication
        df = df[["player_id", "player_name", "total_earnings", "main_game", "earnings_percent"]]
        df = df.drop_duplicates()

        insert_into_mysql(df, "players", ["player_id", "player_name", "total_earnings", "main_game", "earnings_percent"])
    else:
        print("❌ Failed to fetch player data.")

def scrape_tournaments():
    print("\n🏆 Scraping Top Tournaments (First 4 Columns Only)")

    urls = [
        'https://www.esportsearnings.com/tournaments/largest-overall-prize-pools',
        'https://www.esportsearnings.com/tournaments/largest-overall-prize-pools-x100',
        'https://www.esportsearnings.com/tournaments/largest-overall-prize-pools-x200',
        'https://www.esportsearnings.com/tournaments/largest-overall-prize-pools-x300',
        'https://www.esportsearnings.com/tournaments/largest-overall-prize-pools-x400'
    ]

    dfs = []

    for url in urls:
        try:
            tables = pd.read_html(url)
            if tables:
                dfs.append(tables[0])
            else:
                print(f"⚠️ No table found at: {url}")
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)

        # Only take the first 4 columns: rank, tournament_name, prize_pool, game
        combined_df = combined_df.iloc[:, :4]
        combined_df.columns = ["rank", "tournament_name", "prize_pool", "game"]

        # Clean prize pool
        combined_df["prize_pool"] = combined_df["prize_pool"].replace(r'[\$,]', '', regex=True).astype(float).astype(int)

        # Final DataFrame for MySQL and deduplication
        final_df = combined_df[["tournament_name", "prize_pool", "game"]].drop_duplicates()

        # Insert into MySQL
        insert_into_mysql(final_df, "tournaments", ["tournament_name", "prize_pool", "game"])

    else:
        print("❌ No tournament data fetched.")

def scrape_teams():
    print("\n🎮 Scraping Teams")
    
    # Prepare URLs for 500 rows (in 100 increments)
    urls = [f"https://www.esportsearnings.com/teams/highest-overall-x{i}" if i else
            "https://www.esportsearnings.com/teams/highest-overall" for i in range(0, 500, 100)]
    
    df = fetch_multiple_tables(urls)

    if df is not None:
        print(f"📊 Available columns in scraped 'teams': {list(df.columns)}")

        # Rename columns manually
        df.columns = ["rank", "team_name", "revenue", "tournaments_played"]

        # Clean monetary and numeric fields
        df["team_name"] = df["team_name"].astype(str)
        df["revenue"] = df["revenue"].replace(r'[\$,]', '', regex=True).astype(float).astype(int)
        df["tournaments_played"] = df["tournaments_played"].astype(str).str.replace(" Tournaments", "").str.replace(",", "")
        df["tournaments_played"] = pd.to_numeric(df["tournaments_played"], errors='coerce').fillna(0).astype(int)

        # Final cleaned DataFrame and deduplication
        df = df[["team_name", "revenue", "tournaments_played"]].drop_duplicates()

        insert_into_mysql(df, "teams", ["team_name", "revenue", "tournaments_played"])
    else:
        print("\n📁 Data successfully saved to 'top_500_esports_players.csv'")
        print("❌ Failed to fetch team data.")

# ========== Main ==========
def main():
    print("🚀 Starting Esports Scraper + DB Inserter")
    init_database()
    scrape_countries()
    scrape_players()
    scrape_tournaments()
    scrape_teams()
    print("\n✅ All data scraped and inserted successfully!")

# Function to get SQLAlchemy engine

def get_engine():
    return create_engine("mysql+pymysql://root:@localhost/esports_data")

# Function to import CSV into database table

def import_csv_to_db(csv_path, table_name, engine, if_exists='append'):
    """
    Import a CSV file into a MySQL table using pandas and SQLAlchemy.
    - csv_path: path to the CSV file
    - table_name: name of the table in the database
    - engine: SQLAlchemy engine
    - if_exists: 'append' to add, 'replace' to overwrite
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"✅ Imported {csv_path} to {table_name} ({len(df)} rows)")

if __name__ == "__main__":
    # Uncomment the following lines to import CSVs when running this script
    engine = get_engine()
    import_csv_to_db('VideoGames.csv', 'VideoGames', engine)
    import_csv_to_db('Steam.csv', 'SteamData', engine)
    import_csv_to_db('Gaming_trends.csv', 'GamingTrends', engine)
    main()
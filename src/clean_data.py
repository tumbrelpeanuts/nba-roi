import pandas as pd
from pathlib import Path
import unicodedata
from unidecode import unidecode

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


TEAM_MAP = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BRK",
    "Charlotte Hornets": "CHO", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Washington Wizards": "WAS",
    "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", 
    "Phoenix Suns": "PHO", "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", 
    "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR", "Utah Jazz": "UTA", 
}

def normalize_name(name):
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")


################################################################################
# Cleaning BREF data 
##### 2024-25 NBA Player Stats: Per Game
##### 2024-25 NBA Player Stats: Advanced
################################################################################

def clean_per_game(df):
    df = df[df["Rk"] != "Rk"].copy()

    # Team: team_abbr 
    # team_abbr to match espn data
    df = df.rename(columns={"Player": "player_name", "Team":"team_abbr", "Pos": "pos", "Age": "age"})

    df["player_name"] = (
        df["player_name"]
        .str.replace(r"\*$", "", regex=True)
        .str.strip()
        .apply(unidecode)
    )

    # Traded players — BBRef uses TOT, 2TM, or 3TM for multi-team totals
    # Removing duplicates traded players
    traded = {"TOT", "2TM", "3TM"} 
    df_tot = df[df["team_abbr"].isin(traded)] 
    df_single = df[~df["player_name"].isin(df_tot["player_name"])]
    df = pd.concat([df_single, df_tot], ignore_index=True)

    num_cols = ["age", "G", "GS", "MP", "FG%", "3P%", "FT%", "TRB", "AST", "STL", 
                "BLK", "TOV", "PTS"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # df = df[df["player_name"] != "League Average"]
    keep = ["player_name", "team_abbr", "pos", "age", "G", "GS", "MP", "FG%", 
            "3P%", "FT%", "TRB", "AST", "STL", "BLK", "TOV", "PTS"]    
    return df[keep].reset_index(drop=True)



def clean_advanced(df):
    df = df[df["Rk"] != "Rk"].copy()

    # Team: team_abbr 
    # team_abbr to match espn data
    df = df.rename(columns={"Player": "player_name", "Team":"team_abbr"})

    df["player_name"] = (
        df["player_name"]
        .str.replace(r"\*$", "", regex=True)
        .str.strip()
        .apply(unidecode) # to fix Nikola Jokić. W/out, we get Nikola JokiÄ
    )

    # Traded players — BBRef uses TOT, 2TM, or 3TM for multi-team totals
    # Removing duplicates traded players
    traded = {"TOT", "2TM", "3TM"} 
    df_tot = df[df["team_abbr"].isin(traded)] # team_abbr
    df_single = df[~df["player_name"].isin(df_tot["player_name"])]
    df = pd.concat([df_single, df_tot], ignore_index=True)

    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    num_cols = ["PER", "TS%", "USG%", "WS", "WS/48", "BPM", "VORP"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")


    # df = df[df["player_name"] != "League Average"]
    keep = ["player_name", "team_abbr", "PER", "TS%", "USG%", "WS", "WS/48", 
            "BPM", "VORP"]
    return df[keep].reset_index(drop=True)


def clean_bref_data():
    per_game_raw = pd.read_csv(RAW_DATA_DIR / "bref_per_game_stats.csv")
    advanced_raw = pd.read_csv(RAW_DATA_DIR / "bref_advanced_stats.csv")

    clean_per = clean_per_game(per_game_raw)
    clean_adv_game = clean_advanced(advanced_raw)

    clean_per.to_csv(PROCESSED_DATA_DIR / "bref_per_game_stats.csv", index=False)
    print(f"Saved bref_per_game_stats.csv to data/processed")

    clean_adv_game.to_csv(PROCESSED_DATA_DIR / "bref_advanced_stats.csv", index=False)
    print(f"Saved bref_advanced_stats.csv to data/processed")



################################################################################
# Cleaning ESPN Salaries
##### NBA Player Salaries - 2024-2025
################################################################################

def clean_espn(df):

    columns = ["rank", "name", "team", "salary"]
    df.columns = columns
    
    # RK	NAME	TEAM	SALARY
    # Filtering out those rows above
    df = df[df["rank"] != "RK"].copy()

    # skip empty pages
    if df.empty:
        return df
    
    # Stephen Curry, G
    # split into name and position
    split = df["name"].str.rsplit(", ", n=1, expand=True)
    df["player_name"] = split[0]
    df["position"] = split[1]

    # map abbrevations to their respective team
    df["team_abbr"] = df["team"].map(TEAM_MAP)

    # cleaning salary: it's in string
    # $9,423,869
    # strip symbols and cast to int
    df["salary"] = (
        df["salary"]
        #.str.strip()
        .str.replace(r"[$,]", "", regex=True)
        .astype(int)
    )
    
    df["rank"] = df["rank"].astype(int)

    new_col = ["rank", "player_name", "position", "team", "team_abbr", "salary"]
    return df[new_col]


def clean_espn_data():
    espn_raw = pd.read_csv(RAW_DATA_DIR / "espn_salaries.csv")

    espn_clean = clean_espn(espn_raw)

    espn_clean.to_csv(PROCESSED_DATA_DIR / "espn_salaries.csv", index=False)
    print(f"Saved espn_salaries.csv to data/processed")



################################################################################
# Cleaning NBA Standings
##### NBA Standings
################################################################################

def clean_standings(df):
    df["team_name"] = df["TeamCity"] + " " + df["TeamName"]
    df["team_abbr"] = df["team_name"].map(TEAM_MAP)

    df["overall_rank"] = df["WinPCT"].rank(ascending=False, method="min").astype(int)

    df = df.rename(columns={
        "WINS": "wins", 
        "LOSSES": "losses",
        "WinPCT": "Win_PCT",
        "HOME": "home_record",
        "ROAD": "road_record",
        "Conference": "conference"
    })


    keep = ["team_abbr", "team_name", "wins", "losses", "Win_PCT", "home_record",
             "road_record", "conference", "overall_rank"]
    return df[keep].reset_index(drop=True)


def clean_standings_data():
    standings_raw = pd.read_csv(RAW_DATA_DIR / "standings.csv")

    standings_clean = clean_standings(standings_raw)

    missing = standings_clean[standings_clean["team_abbr"].isna()] 
    if not missing.empty: 
        print(f"{len(missing)} teams missing abbreviation mapping:") 
        print(missing["team_name"].tolist())
    else:
        print(f"Team mapped successfully")

    standings_clean.to_csv(PROCESSED_DATA_DIR / "standings.csv", index=False)
    print(f"Saved standings.csv to data/processed")



################################################################################
### Calling All Cleaning Functions
################################################################################

def main():
    clean_bref_data()
    clean_espn_data()
    clean_standings_data()
    clean_espn_data()



if __name__ == "__main__":
    main()

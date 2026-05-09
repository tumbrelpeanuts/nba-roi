import pandas as pd
from pathlib import Path
from scraper_bref import scrape as scraper_bref
from scraper_espn import scrape as scraper_espn
from scraper_nba_api import scrape as scraper_nba_api
from scrape_bref_teams import scrape as scraper_player_exp

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


### Basketball Reference
def bbref():
    print("### Fetching Basketball-Reference data ###")
    per_game, adv_game = scraper_bref()
    
    per_game.to_csv(RAW_DATA_DIR / "bref_per_game_stats.csv", index=False, encoding="utf-8")
    print(f"Saved bref_per_game_stats.csv to data/raw")
    
    adv_game.to_csv(RAW_DATA_DIR / "bref_advanced_stats.csv", index=False, encoding="utf-8")
    print(f"Saved bref_advanced_stats.csv to data/raw")


### ESPN
def espn():
    print("\n\n### Fetching ESPN Player Salary data ###")
    df_espn = scraper_espn()
    df_espn.to_csv(RAW_DATA_DIR / "espn_salaries.csv", index=False)
    print(f"Saved espn_salaries.csv to data/raw")


### NBA_API
def nba_api():
    print("\n\n### Fetching NBA Team Standings data ###")
    df_api = scraper_nba_api()
    df_api.to_csv(RAW_DATA_DIR / "standings.csv", index=False)
    print("Saved standings.csv to to data/raw")


### Basketball Reference Player's Years of Experience
def player_exp():
    print("\n\n### Fetching Player's Years of Experience data ###")
    df_exp = scraper_player_exp()
    df_exp.to_csv(RAW_DATA_DIR / "player_exp.csv", index=False)
    print("Saved player_exp.csv to to data/raw") 


def main():
    ### Basketball-Reference data
    bbref()

    ### ESPN ESPN Player Salary data 
    espn()

    ###  NBA Team Standings data
    nba_api()

    ### Player's Years of Experience
    player_exp()


if __name__ == "__main__":
    main()

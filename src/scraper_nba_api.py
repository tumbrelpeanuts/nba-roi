import pandas as pd
from pathlib import Path
from nba_api.stats.endpoints import leaguestandingsv3

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

def scrape():
    print("Fetching 2024-25 NBA standings from nba_api ...")
    standings = leaguestandingsv3.LeagueStandingsV3(
        league_id = "00", 
        season="2024-25",
        season_type="Regular Season"
    )

    df = standings.get_data_frames()[0]
    return df


def main():
    df = scrape()

    df.to_csv(RAW_DATA_DIR / "standings.csv", index=False)
    print("Saved standings.csv to to data/raw")

if __name__ == "__main__":
    main()
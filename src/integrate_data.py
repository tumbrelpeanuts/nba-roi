import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"


def load_data():
    per_game = pd.read_csv(PROCESSED_DATA_DIR / "bref_per_game_stats.csv")
    advanced = pd.read_csv(PROCESSED_DATA_DIR / "bref_advanced_stats.csv")
    salaries = pd.read_csv(PROCESSED_DATA_DIR / "espn_salaries.csv")
    standings = pd.read_csv(PROCESSED_DATA_DIR / "standings.csv")
    
    return per_game, advanced, salaries, standings


def remove_traded_players(per_game, advanced):
    traded = {"TOT", "2TM", "3TM"} 

    # Count before removing
    traded_players = per_game[per_game["team_abbr"].isin(traded)]
    print(f"Traded/multi-team players removed: {len(traded_players)}")

    per_game = per_game[~per_game["team_abbr"].isin(traded)].copy()
    advanced = advanced[~advanced["team_abbr"].isin(traded)].copy()

    return per_game, advanced


def integrate():
    per_game, advanced, salaries, standings = load_data()
    per_game = per_game[per_game["player_name"] != "League Average"]
    advanced = advanced[advanced["player_name"] != "League Average"]
    per_game, advanced = remove_traded_players(per_game, advanced)

    # Join 1 per_game + advanced stat
    bref = pd.merge(per_game, advanced, on=["player_name", "team_abbr"], how="inner")
    print(f"After bref join: {len(bref)} players")


    # Join 2
    master = pd.merge(bref, salaries[["player_name", "team_abbr", "salary"]], 
                    on=["player_name", "team_abbr"], how="inner")
    print(f"After salary join: {len(master)} players. New dataframe is called master")
    
    # Join 3
    master = pd.merge(master, standings, on="team_abbr", how="left")
    print(f"After standings join: {len(master)} players")

    # win share per million
    master["ws_per_million"] = master["WS"] / (master["salary"] / 1000000)

    # players that didn't match with standings
    missing_teams = master[master["Win_PCT"].isna()]["team_abbr"].unique()
    if len(missing_teams) > 0:
        print(f"{len(missing_teams)} team missing from standings: {missing_teams.tolist()}")
    else:
        print("All teams matched with standings")

    return master



def main():
    master = integrate()

    master.to_csv(PROCESSED_DATA_DIR / "master.csv", index=False)
    print("Saved master.csv to data/processed")



if __name__ == "__main__":
    main()
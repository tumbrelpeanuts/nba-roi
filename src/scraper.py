import argparse
import pandas as pd
import requests
import sys
import time
import io
from tqdm import tqdm # to see if webscraping progress

URL = "https://www.espn.com/nba/salaries/_/year/2025/page/"


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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


def get_page(page_num: int):
    url = f"https://www.espn.com/nba/salaries/_/year/2025/page/{page_num}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    table = pd.read_html(io.StringIO(response.text), attrs={"class": "tablehead"})
    return table[0]

def parse_table(df):
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


def scrape(limit=None):
    all_rows = []

    # for page in range(1,15): 
    for page in tqdm(range(1, 15), desc="Scraping pages"): # pages 1-3, see if sleep bypasses block
        df = get_page(page)

        if df is None: # page failed or doesn't exist, stop early
            break

        clean_df = parse_table(df)

        for _, row in clean_df.iterrows():
            all_rows.append(row)
            if limit is not None and len(all_rows) >= limit: # early exit if row cap hit
                return pd.DataFrame(all_rows).reset_index(drop=True)
        
        time.sleep(3) # wait 3 seconds in between pages

    return pd.DataFrame(all_rows).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Scrape NBA salary data from EPSN")
    parser.add_argument("--scrape", type =int, metavar="N", help="Scrape only the first N entries")
    parser.add_argument("--save", type=str, metavar="PATH", help="Save the results in a csv file at")
    args = parser.parse_args()

    if args.scrape:
        df = scrape(limit=args.scrape)
        print(df.to_string(index=False))
    elif args.save:
        df = scrape()
        df.to_csv(args.save, index=False)
        print(f"Saved {len(df)} records to {args.save}")
    else:
        df = scrape()
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
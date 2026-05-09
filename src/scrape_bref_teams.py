import pandas as pd
import requests
import time
import io
from tqdm import tqdm # to see if webscraping progress
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

TEAMS = ['ATL','BOS','BRK','CHO','CHI','CLE','DAL','DEN','DET','GSW',
         'HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK',
         'OKC','ORL','PHI','PHO','POR','SAC','SAS','TOR','UTA','WAS']


def fetch_table(url, table_id, team):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"  # force UTF-8 decoding

    tables = pd.read_html(io.StringIO(response.text), attrs={"id": table_id}, flavor="lxml")
    df = tables[0]
    df['team_abbr'] = team
    return df


def scrape():
    all_pages = []

    for team in tqdm(TEAMS, desc="Scraping Basketball-Reference Team pages"):  
        url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
        print("Scraping team ...")
        player = fetch_table(url, "roster", team)

        all_pages.append(player)
        time.sleep(1.2)

    return pd.concat(all_pages, ignore_index=True)


def main():
    df = scrape()
    df.to_csv(RAW_DATA_DIR / "player_exp.csv", index=False)
    print(f"Saved player_exp.csv to data/raw")


if __name__ == "__main__":
    main()
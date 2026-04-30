
import pandas as pd
import requests
import time
import io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

PER_GAME_URL = "https://www.basketball-reference.com/leagues/NBA_2025_per_game.html"
ADV_URL = "https://www.basketball-reference.com/leagues/NBA_2025_advanced.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


def fetch_table(url, table_id):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"  # force UTF-8 decoding

    tables = pd.read_html(io.StringIO(response.text), attrs={"id": table_id}, flavor="lxml")
    return tables[0]


def scrape():
    print("Scraping per_game ...")
    per_game = fetch_table(PER_GAME_URL, "per_game_stats")
    time.sleep(4) # prevent from being blocked

    print("Scraping advanced ...")
    adv_game = fetch_table(ADV_URL, "advanced")

    return per_game, adv_game

def main():
    per_game, adv_game = scrape()

    per_game.to_csv(RAW_DATA_DIR / "bref_per_game_stats.csv", index=False, encoding="utf-8")
    print(f"Saved bref_per_game_stats.csv to data/raw")

    adv_game.to_csv(RAW_DATA_DIR / "bref_advanced_stats.csv", index=False, encoding="utf-8")
    print(f"Saved bref_advanced_stats.csv to data/raw")


if __name__ == "__main__":
    main()

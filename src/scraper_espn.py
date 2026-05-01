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


def get_page(page_num: int):
    # "https://www.espn.com/nba/salaries/_/year/2025/page/"
    url = f"https://www.espn.com/nba/salaries/_/year/2025/page/{page_num}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    table = pd.read_html(io.StringIO(response.text), attrs={"class": "tablehead"})
    return table[0]


def scrape():
    all_pages = []

    # for page in range(1,15): 
    for page in tqdm(range(1, 15), desc="Scraping ESPN pages"): # pages 1-3, see if sleep bypasses block
        df = get_page(page)

        all_pages.append(df)
        time.sleep(1.2) # wait 3 seconds in between pages

    return pd.concat(all_pages, ignore_index=True)


def main():
    df = scrape()
    df.to_csv(RAW_DATA_DIR / "espn_salaries.csv", index=False)
    print(f"Saved espn_salaries.csv to data/raw")


if __name__ == "__main__":
    main()
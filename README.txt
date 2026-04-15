README — ESPN NBA Salary Scraper
=================================
DSCI 510 | Submission 2 | Alexander Sanchez

Link to my GitHub repo: https://github.com/tumbrelpeanuts/nba-roi
The README.md is easier to read.

What the web scrape script does
-------------

The script scraper.py scrapes the 2024-2025 players' salaries from ESPN's salary page [(https://www.espn.com/nba/salaries/_/year/2025)](https://www.espn.com/nba/salaries/_/year/2025/). It paginates through 14 pages using requests and pd.read_html(), extracting each player's rank, name, position, team, and salary. The salaries are returned as strings, such as "$9,423,869." I had to remove the $ and the comma and convert them to integers. I created team abbreviations ("Atlanta Hawks": "ATL") to make joining with other data sources easier.

Requirements
-------------
Python 3.13

Packages are managed with uv (https://docs.astral.sh/uv/).

Install uv

Mac/Linux:
    curl -LsSf https://astral.sh/uv/install.sh | sh

Windows:
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


Install dependencies:
    uv sync



How to run it
-------------

1. Print all players stdout:
    uv run python src/scraper.py

2. Print all the first N players:
    uv run python src/scraper.py --scrape 10

3. Save all players to a csv file:
    uv run python src/scraper.py --save data/raw/salaries.csv

**NOTE**: I used sleep because the site sometimes rate-limits. The script waits three seconds between pages to avoid being rate-limited by ESPN. As a result, a full scrape takes about 45 seconds. You can probably lower the wait time. I set it high as a precaution.


Note on source change
-------------
The original proposal used HypeHoop (https://www.hoopshype.com/salaries/players/?season=2024) as the salary data source via its GraphQL API. When writing the script, it returned 401 Unauthorized errors, blocking all API access. I switched to ESPN's salary page as a replacement. It provides the same salary data and is publicly accessible.
# NBA Salary Analysis Project
DSCI 510 | Final Project | Alexander Sanchez

---

## Overview

This project analyzes NBA player salaries by combining multiple web data sources. The goal is to explore patterns in salaries across teams, positions, and other factors.

---

## Data Sources

- ESPN Salaries
  - https://www.espn.com/nba/salaries/_/year/2025
- NBA Game Standings
  - https://github.com/swar/nba_api
- BBREF NBA Player Stats: Per Game and Advanced 
  - https://www.basketball-reference.com/leagues/NBA_2025_per_game.html
  - https://www.basketball-reference.com/leagues/NBA_2025_advanced.html


Note on source change
* The original proposal used HypeHoop (https://www.hoopshype.com/salaries/players/?season=2024) as the salary data source via its GraphQL API. When writing the script, it returned 401 Unauthorized errors, blocking all API access. I switched to ESPN's salary page as a replacement. It provides the same salary data and is publicly accessible.

---

## Setup Instructions

### Install uv

Mac/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Create environment & install dependencies

```bash
uv sync
```

**Alternative (without uv):**

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
data/
  raw/        # raw scraped data
  processed/  # cleaned data

src/
  get_data.py
  clean_data.py
  integrate_data.py
  analyze_visualize.py
  scraper_bref.py
  scraper_espn.py
  scraper_nba_api.py
  utils/
    constants.py
    helpers.py

results/
  correlation_heatmap.png
  team_payroll_vs_winpct.png
  team_ws_per_million.png
  actual_vs_expected_salary.png
  dumbbell_salary_comparison.png
```

---

## Data Collection

Run:

```bash
uv run python src/get_data.py
```

This will:

* Scrape ESPN paler's salary data from 2024-25 season
* Scrape NBA team standings from NBA API
* Scrape Basketball-Reference NBA Player Stats per-game & advanced stats
* Save to `data/raw/`

**NOTE**: I used sleep because the site sometimes rate-limits. The script waits one second between pages to avoid being rate-limited by ESPN. As a result, a full scrape takes about 15 seconds.

---

## Data Cleaning

Run:

```bash
uv run python src/clean_data.py
```

This will:

* Basketball-Reference
  * Remove repeated header rows and deduplicate traded players (`TOT`/`2TM`/`3TM`)
  * Normalize player names (handles accented characters)
* ESPN Salary
  * Convert salary strings → numeric
  * Standardize team names
* NBA Team Standings
* Output cleaned data to `data/processed/`

---

## Data Integration

Run:

```bash
uv run python src/integrate_data.py
```

This will:

* Merge multiple data sources
* Create a unified dataset for analysis

---

## Analysis & Visualization

Run:

```bash
uv run python src/analyze_visualize.py
```

This will:

* Generate summary statistics
* Create visualizations (plots/graphs)


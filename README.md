# NBA Salary Analysis Project
DSCI 510 | Final Project | Alexander Sanchez

---

## Overview

This project investigates NBA salary efficiency for the 2024–25 season: which teams get the most value per dollar spent and which players are undervalued relative to their on-court production. Data was collected from Basketball-Reference (player performance stats and years of experience), ESPN (player salaries), and the NBA API (team standings), then cleaned, integrated, and analyzed in Python. The pipeline automatically scrapes and processes all data, fits a per-position regression model to estimate expected salaries, and produces six visualizations that explore the relationship between payroll and performance at both the player and team levels.

---

## Data Sources

- ESPN Salaries
  - https://www.espn.com/nba/salaries/_/year/2025
- NBA Game Standings
  - https://github.com/swar/nba_api
- BBREF NBA Player Stats: Per Game and Advanced 
  - https://www.basketball-reference.com/leagues/NBA_2025_per_game.html
  - https://www.basketball-reference.com/leagues/NBA_2025_advanced.html
- BBREF all NBA team rosters for the 2024-25 season
  - https://www.basketball-reference.com/teams
  - https://www.basketball-reference.com/teams/{team}/2025.html
  - where team is NBA team abbrevation


Note on source change
* The original proposal used HypeHoop (https://www.hoopshype.com/salaries/players/?season=2024) as the salary data source via its GraphQL API. When writing the script, it returned 401 Unauthorized errors, blocking all API access. I switched to ESPN's salary page as a replacement. It provides the same salary data and is publicly accessible.
* ESPN implemented AWS WAF bot protection. The scraper was updated to use Playwright

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
uv run playwright install chromium
```

**Alternative (without uv):**

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## How to Run the Project (End-to-End)

Run the following commands in order:

```bash
uv run python src/get_data.py
uv run python src/clean_data.py
uv run python src/integrate_data.py
uv run python src/analyze_visualize.py
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
  scrape_bref_teams.py
  scraper_espn.py
  scraper_nba_api.py
  utils/
    constants.py
    helpers.py

results/
  final_report.pdf
  correlation_heatmap.png
  team_payroll_vs_winpct.png
  team_ws_per_million.png
  actual_vs_expected_salary.png
  dumbbell_salary_diff_comparison.png
  dumbbell_salary_diff-pct_comparison.png
```

---

## Data Collection

Run:

```bash
uv run python src/get_data.py
```

This will:

* Scrape ESPN player's salary data from 2024-25 season
* Scrape NBA team standings from NBA API
* Scrape Basketball-Reference NBA Player Stats per-game & advanced stats
* Scrape Basketball-Reference team roster pages for all 30 NBA teams to extract each player's years of experience
* Save to `data/raw/`
  * espn_salaries.csv 
  * standings.csv 
  * bref_per_game_stats.csv
  * bref_advanced_stats.csv 
  * player_exp.csv

**NOTE**: The scraper waits ~1.2 seconds between team pages to avoid being rate-limited by Basketball-Reference. A full scrape of all 30 teams takes roughly 40 seconds.

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
  * Remove repeated header rows
  * Convert salary strings → numeric
  * Standardize team names
* NBA Team Standings
  * Standardize team names
  * Compute overall rank by win percentage
* Output cleaned data to `data/processed/`
  * bref_advanced_stats.csv 
  * espn_salaries.csv 
  * standings.csv 
  * bref_per_game_stats.csv
  * player_exp.csv

---

## Data Integration

Run:

```bash
uv run python src/integrate_data.py
```

This will:

* Merge per-game stats + advanced stats (on `player_name`, `team_abbr`)
* Join with ESPN salaries, then team standings
* Compute `ws_per_million` (win shares per $1M salary)
* Output `master.csv` to `data/processed/`

---

## Analysis & Visualization

Run:

```bash
uv run python src/analyze_visualize.py
```

This will:

* Fit a linear regression to estimate expected salary from performance stats
* Generate and save plots to `results/`:
  * `correlation_heatmap.png` — correlations between salary, stats, and efficiency
  * `team_payroll_vs_winpct.png` — team payroll vs win percentage
  * `team_ws_per_million.png` — team salary efficiency (WS per $1M)
  * `actual_vs_expected_salary.png` — actual vs model-predicted salary by position
  * `dumbbell_salary_diff_comparison.png` — top 15 most underpaid players
  * `dumbbell_salary_diff-pct_comparison.png` - top 15 most underpaid players by percentage gap, excluding CBA-mandated minimum contracts

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

from utils.constants import POSITION_COLORS, POSITION, TIER_COLORS
from utils.helpers import millions, build_analysis_df, build_team_df
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def plot_correlation_heatmap(df):
    """Heatmap of correlations between salary, performance stats, and efficiency."""
    cols = ["salary", "PTS", "TRB", "AST", "WS", "PER", "BPM", "VORP", "ws_per_million"]
 
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation: Performance Stats vs Salary", fontsize=14)
 
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "correlation_heatmap.png", dpi=150)
    # plt.show()
    print("Saved correlation_heatmap.png")
 
 
def plot_team_payroll_vs_wins(team):
    """Scatter: team total salary vs win%, with regression line."""
    fig, ax = plt.subplots(figsize=(12, 8))
 
    sns.scatterplot(data=team, x="total_salary", y="Win_PCT",
                    ax=ax, s=100, color="steelblue")
    sns.regplot(data=team, x="total_salary", y="Win_PCT",
                scatter=False,
                line_kws={"color": "red", "linewidth": 1.5, "linestyle": "--"},
                ax=ax)
    
    manual_offsets = { "GSW": (-15, -10), 
                      "MEM": (5, 5), 
                      "CHI": (5, -10), 
                      "DAL": (5, 5)
                      }               
    for _, row in team.iterrows():
        abbr = row["team_abbr"]
        xytext = manual_offsets.get(abbr, (5, 5))
        ax.annotate(row["team_abbr"], (row["total_salary"], row["Win_PCT"]),
                    textcoords="offset points", xytext=xytext, fontsize=8)
 
    ax.set_title("Team Payroll vs Win%\n(dashed line = expected win% given spend)", fontsize=14)
    ax.set_xlabel("Total Salary (Millions USD)")
    ax.set_ylabel("Win %")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(millions))

    # remove axis splines
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)
 
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "team_payroll_vs_winpct.png", dpi=150)
    # plt.show()
    print("Saved team_payroll_vs_winpct.png")

 
def plot_team_ws_per_million(team):
    """Horizontal bar chart ranking teams by average WS per $1M spent."""
    team_ranked = team.sort_values("team_ws_per_million", ascending=True)
    top5 = team_ranked.nlargest(5, "team_ws_per_million")["team_abbr"].tolist()
 
    fig, ax = plt.subplots(figsize=(10, 10))
 
    bars = ax.barh(team_ranked["team_abbr"], team_ranked["team_ws_per_million"],
                   color="steelblue")
    for bar, abbr in zip(bars, team_ranked["team_abbr"]):
        if abbr in top5:
            bar.set_color("#FF9800")
 
    ax.set_title("Team Salary Efficiency: WS per $1M Spent\n(orange = top 5 most efficient)", fontsize=14)
    ax.set_xlabel("Win Shares per $1M")
    ax.set_ylabel("")

    # remove axis splines
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)
 
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "team_ws_per_million.png", dpi=150)
    # plt.show()
    print("Saved team_ws_per_million.png")
 
 
def plot_actual_vs_expected_salary(df_temp):
    """Scatter: actual salary vs model-predicted salary. Below diagonal = underpaid."""
    fig, ax = plt.subplots(figsize=(12, 8))
 
    sns.scatterplot(data=df_temp, x="expected_salary", y="salary",
                    hue="position_full", palette=POSITION_COLORS, alpha=0.7, ax=ax)
 
    max_val = max(df_temp["expected_salary"].max(), df_temp["salary"].max())
    ax.plot([0, max_val], [0, max_val], color="black", linewidth=1.5,
            linestyle="--", label="Fair value (actual = expected)")
 
    most_underpaid = df_temp.nlargest(5, "salary_diff")
    for _, row in most_underpaid.iterrows():
        ax.annotate(row["player_name"], (row["expected_salary"], row["salary"]),
                    textcoords="offset points", xytext=(5, -10), fontsize=8)
 
    ax.set_title("Actual vs Expected Salary\n(below the line = underpaid relative to stats)", fontsize=14)
    ax.set_xlabel("Market Value Estimate (Millions USD)")
    ax.set_ylabel("Actual Salary (Millions USD)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(millions))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions))
    ax.legend()

    # remove axis splines
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)
 
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "actual_vs_expected_salary.png", dpi=150)
    # plt.show()
    print("Saved actual_vs_expected_salary.png")
 


def plot_dumbbell_salary_diff(df_temp):
    top15 = df_temp.nlargest(15, "salary_diff").sort_values("salary_diff")

    actual = top15["salary"] / 1_000_000
    expected = top15["expected_salary"] / 1_000_000
    players = top15["player_name"]

    y_pos = range(len(top15))

    fig, ax = plt.subplots(figsize=(10, 7))

    # draw connecting lines
    for i, (a, e) in enumerate(zip(actual, expected)):
        ax.plot([a, e], [i, i], color="gray", linewidth=2, zorder=1)

    # actual salary dots
    ax.scatter(actual, y_pos, color="steelblue", s=60, label="Actual Salary", zorder=2)

    # expected salary dots
    ax.scatter(expected, y_pos, color="#FF9800", s=60, label="Expected Salary", zorder=3)

    # labels
    offset = 1.85
    for i, (a, e) in enumerate(zip(actual, expected)):
        ax.text(a - offset, i, f"{a:.0f}", va="center", ha="right", fontsize=9)
        ax.text(e + offset, i, f"{e:.0f}", va="center", ha="left", fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(players)
    
    ax.set_title("Most Underpaid Players by Dollar Amount (Actual vs Expected Salary)", fontsize=14)
    ax.set_xlabel("Salary (Millions USD)")
    
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        frameon=False
    )

    # remove axis splines
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)

    #
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig(RESULTS_DIR / "dumbbell_salary_diff_comparison.png", dpi=150, bbox_inches="tight")
    # plt.show()
    print("Saved dumbbell_salary_diff_comparison.png")



def plot_dumbbell_salary_pct_diff(df_temp):
    # df_temp = df_temp[df_temp["salary"] >= 2_000_000] # 
    df_temp = df_temp[df_temp["salary"] >= df_temp["cba_minimum"] * 1.1]
    '''Players on CBA-mandated minimum contracts were excluded from the percentage 
    gap analysis because their salaries are not performance-based.'''
    
    top15 = df_temp.nlargest(15, "salary_pct_diff").sort_values("salary_pct_diff", ascending=True)

    actual = top15["salary"] / 1_000_000
    expected = top15["expected_salary"] / 1_000_000
    players = top15["player_name"]

    y_pos = range(len(top15))
    fig, ax = plt.subplots(figsize=(10, 7))

    # draw connecting lines
    for i, (a, e) in enumerate(zip(actual, expected)):
        ax.plot([a, e], [i, i], color="gray", linewidth=2, zorder=1)

    # actual salary dots
    ax.scatter(actual, y_pos, color="steelblue", s=60, label="Actual Salary", zorder=2)

    # expected salary dots
    ax.scatter(expected, y_pos, color="#FF9800", s=60, label="Expected Salary", zorder=3)

    # labels
    x_range = expected.max() - actual.min()
    offset = x_range * 0.015
    for i, (a, e) in enumerate(zip(actual, expected)):
        ax.text(a - offset, i, f"{a:.1f}", va="center", ha="right", fontsize=9)
        ax.text(e + offset, i, f"{e:.1f}", va="center", ha="left", fontsize=9)
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(players)
    
    ax.set_title("Most Underpaid Players by % Below Expected Salary", fontsize=14)
    ax.set_xlabel("Salary (Millions USD)")
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        frameon=False
    )

    # remove axis splines
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)

    #plt.tight_layout()
    # ax.set_xlim(left=-0.5)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig(RESULTS_DIR / "dumbbell_salary_diff-pct_comparison.png", dpi=150, bbox_inches="tight")
    # plt.show()
    print("Saved dumbbell_salary_diff-pct_comparison.png")


# def dot_plot():
# WS per $1M by position
# Average underpaid gap by position
# Distribution salaries by position

def main():
    # load
    df = pd.read_csv(PROCESSED_DATA_DIR / "master.csv")
    print(f"Loaded master.csv: {len(df)} players")
 
    # build analysis dataframes
    df_temp = build_analysis_df(df)
    team    = build_team_df(df)
 
    # generate all plots
    plot_correlation_heatmap(df_temp)
    plot_team_payroll_vs_wins(team)
    plot_team_ws_per_million(team)
    plot_actual_vs_expected_salary(df_temp)
    plot_dumbbell_salary_diff(df_temp)
    plot_dumbbell_salary_pct_diff(df_temp)
 
    print(f"\nAll plots saved to {RESULTS_DIR}")
 
 
if __name__ == "__main__":
    main()
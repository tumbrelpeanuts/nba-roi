import numpy as np
from sklearn.linear_model import LinearRegression
from utils.constants import POSITION_MAP, FEATURES


def millions(x, pos):
    return f"${x/1e6:.0f}M"


def adjusted_r2(r2, n, k):
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)


def fit_position_model(group, features):
    """Fit log-linear regression per position, return group with expected_salary."""
    group = group.copy()
    if len(group) <= len(features) + 1:
        group["expected_salary"] = np.nan
        return group
    log_y = np.log(group["salary"])
    model = LinearRegression().fit(group[features], log_y)
    group["expected_salary"] = np.exp(model.predict(group[features]))
    return group


def build_analysis_df(df):
    """Filter master df and fit per-position salary model."""
    df_temp = df[df["G"] >= 20].copy()
    df_temp["position_full"] = df_temp["pos"].map(POSITION_MAP)

    df_temp = (
        df_temp
        .groupby("position_full", group_keys=False)
        .apply(fit_position_model, features=FEATURES)
        .dropna(subset=["expected_salary"])
    )

    # position_full gets dropped from groupby
    df_temp["position_full"] = df_temp["pos"].map(POSITION_MAP)

    df_temp["salary_diff"]      = df_temp["expected_salary"] - df_temp["salary"]
    df_temp["value_ratio"]      = df_temp["salary"] / df_temp["expected_salary"]
    df_temp["ws_per_million"]   = df_temp["WS"]   / (df_temp["salary"] / 1_000_000)
    df_temp["vorp_per_million"] = df_temp["VORP"]  / (df_temp["salary"] / 1_000_000)

    print(f"Players in analysis dataset: {len(df_temp)}")
    return df_temp


def build_team_df(df):
    """Aggregate player data to team level."""
    team = (
        df.groupby(["team_abbr", "team_name", "Win_PCT"])
        .agg(total_salary=("salary", "sum"), total_ws=("WS", "sum"))
        .reset_index()
    )
    team["team_ws_per_million"] = team["total_ws"] / (team["total_salary"] / 1_000_000)
    return team
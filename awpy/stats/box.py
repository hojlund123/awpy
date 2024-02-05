"""Basic stats for a box-score."""

from typing import Literal

import pandas as pd

from awpy.parser.models.demo import Demo
from awpy.stats.utils import get_player_rounds, get_rounds_played


def kills_per_round(
    demo: Demo, side: Literal["ct", "t", "total"] = "total"
) -> pd.DataFrame:
    """Calculates the Kills per Round (KPR) for each player.

    Args:
        demo (Demo): The demo to calculate the KPR for.
        side (Literal['ct', 't', 'total'], optional): Side to calculate KPR.
            Defaults to "total".

    Returns:
        pd.DataFrame: DataFrame with the KPR for each player
    """
    player_rounds = get_player_rounds(demo.ticks)
    rounds_played = get_rounds_played(player_rounds)
    rounds_played = rounds_played[rounds_played["side"] == side]
    kills_df = (
        demo.kills[demo.kills["attacker_side"] == side]
        .groupby("attacker_steamid")
        .size()
        .reset_index()
        .rename(columns={0: "kills"})
    )
    if side == "total":
        kills_df = (
            demo.kills.groupby("attacker_steamid")
            .size()
            .reset_index()
            .rename(columns={0: "kills"})
        )
    kpr = rounds_played.merge(kills_df, left_on="steamid", right_on="attacker_steamid")
    kpr = kpr[["steamid", "side", "rounds_played", "kills"]]
    kpr["kills"] = kpr["kills"].fillna(0)
    kpr["kills_per_round"] = kpr["kills"] / kpr["rounds_played"]
    return kpr


def deaths_per_round(
    demo: Demo, side: Literal["ct", "t", "total"] = "total"
) -> pd.DataFrame:
    """Calculates the Deaths per Round (DPR) for each player.

    Args:
        demo (Demo): The demo to calculate the DPR for.
        side (Literal['ct', 't', 'total'], optional): Side to calculate SPR.
            Defaults to "total".

    Returns:
        pd.DataFrame: DataFrame with the DPR for each player
    """
    player_rounds = get_player_rounds(demo.ticks)
    rounds_played = get_rounds_played(player_rounds)
    rounds_played = rounds_played[rounds_played["side"] == side]
    deaths_df = (
        demo.kills[demo.kills["victim_side"] == side]
        .groupby("victim_steamid")
        .size()
        .reset_index()
        .rename(columns={0: "deaths"})
    )
    if side == "total":
        deaths_df = (
            demo.kills.groupby("victim_steamid")
            .size()
            .reset_index()
            .rename(columns={0: "deaths"})
        )
    dpr = rounds_played.merge(deaths_df, left_on="steamid", right_on="victim_steamid")
    dpr = dpr[["steamid", "side", "rounds_played", "deaths"]]
    dpr["deaths_per_round"] = dpr["deaths"] / dpr["rounds_played"]
    return dpr


def assists_per_round(
    demo: Demo, side: Literal["ct", "t", "total"] = "total"
) -> pd.DataFrame:
    """Calculates the Assists per Round (APR) for each player.

    Args:
        demo (Demo): The demo to calculate the APR for.
        side (Literal['ct', 't', 'total'], optional): Side to calculate APR.
            Defaults to "total".

    Returns:
        pd.DataFrame: DataFrame with the APR for each player
    """
    player_rounds = get_player_rounds(demo.ticks)
    rounds_played = get_rounds_played(player_rounds)
    rounds_played = rounds_played[rounds_played["side"] == side]
    assists_df = (
        demo.kills[demo.kills["assister_side"] == side]
        .groupby("assister_steamid")
        .size()
        .reset_index()
        .rename(columns={0: "assists"})
    )
    if side == "total":
        assists_df = (
            demo.kills.groupby("assister_steamid")
            .size()
            .reset_index()
            .rename(columns={0: "assists"})
        )
    apr = rounds_played.merge(
        assists_df, left_on="steamid", right_on="assister_steamid"
    )
    apr = apr[["steamid", "side", "rounds_played", "assists"]]
    apr["assists_per_round"] = apr["assists"] / apr["rounds_played"]
    return apr
import re
import time
import random
import math
import statistics
import datetime as dt
import numpy as np
import pandas as pd

comparable_index = [
    "question_id",
    "user_id",
    "team_id",
    "probability",
    "answer_option",
    "timestamp",
    "outcome",
    "open_time",
    "close_time",
    "resolve_time",
    "time_open",
    "n_opts",
    "options",
    "q_status",
    "q_type",
]


def aggregate(
    forecasts,
    aggregation_function,
    on=["question_id", "answer_option"],
    *args,
    **kwargs
):
    """forecasts should be a pandas.DataFrame that contains columns
    question_id, user_id, timestamp, probability, answer_option, outcome, date_closed"""
    # TODO: throw an error if on isn't a subset of columns of forecasts
    aggregations = forecasts.groupby(on).apply(
        _apply_aggregation, aggregation_function, *args, **kwargs
    )
    aggregations.index = aggregations.index.droplevel(["question_id", "answer_option"])
    return aggregations


def _apply_aggregation(group, aggregation_function, *args, **kwargs):
    transformed_probs = np.array(aggregation_function(group, *args, **kwargs))
    return pd.DataFrame(
        {
            "question_id": np.array(group["question_id"])[0],
            "probability": transformed_probs,
            "outcome": np.array(group["outcome"])[0],
            "answer_option": np.array(group["answer_option"])[0],
        }
    )


def score(forecasts, scoring_rule, on=["question_id"], *args, **kwargs):
    # TODO: throw an error if on isn't a subset of columns of forecasts
    scores = forecasts.groupby(on).apply(_apply_score, scoring_rule, *args, **kwargs)
    scores.index = scores.index.droplevel(1)
    return scores


def _apply_score(group, scoring_rule, *args, **kwargs):
    probabilities = np.array(group["probability"])
    outcomes = np.array(group["outcome"])
    options = np.array(group["answer_option"])
    return pd.DataFrame(
        {
            "score": np.array(
                [scoring_rule(probabilities, outcomes == options, *args, **kwargs)]
            )
        }
    )


def normalise(forecasts, on=["question_id"]):
    forecasts = forecasts.groupby(on).apply(_apply_normalise)


def _apply_normalise(group):
    Z = np.sum(group["probability"])
    group["probability"] = group["probability"] / Z
    return group


# This function can't be written in a pandastic way because
# expanding.Expanding.apply only accepts single columns (yes, even with
# numba). I hope future versions will allow for a version of apply that
# plays nicely with expanding. Perhaps I'll find the time to write it.
# Also, it is _slow_: 110 seconds for the 254598 rows of market data
# from the last 2 years.


def add_cumul_user_score(forecasts, scoring_rule, *args, **kwargs):
    forecasts = forecasts.groupby(["user_id"]).apply(
        self._cumul_score, scoring_rule, *args, **kwargs
    )
    forecasts = forecasts.reset_index(drop=True)
    return forecasts


def _cumul_score(group, scoring_rule, *args, **kwargs):
    group = group.sort_values("close_time")
    fst = group.index[0]
    cumul_scores = []
    for lim in group.index:
        expan = group.loc[fst:lim, :]
        cumul_scores.append(
            scoring_rule(
                expan["probability"],
                expan["answer_option"] == expan["outcome"],
                *args,
                **kwargs
            )
        )
    group["cumul_score"] = np.array(cumul_scores)
    return group


# TODO: Maybe make this a tiny bit faster
# Idea: keep resbef, only expand it if necessary, have user_scores
# precomputed as well, only update it if resbef has changed (and if so,
# only with the new resbef values).


def add_cumul_user_perc(forecasts, lower_better=True):
    forecasts = forecasts.sort_values("timestamp")
    fst = forecasts.index[0]
    cumul_rankings = []
    for lim in forecasts.index:
        expan = forecasts.loc[fst:lim, :]
        # timestamp of current forecast
        cur = forecasts.loc[lim:lim, :]
        curts = cur["timestamp"].values[0]
        # get the self.forecasts that have resolved before the current forecast happened
        resbef = expan.loc[expan["close_time"] < curts]
        # get the score of the last resolved forecast each forecaster made before the current forecast
        user_scores = resbef.groupby(["user_id"])["cumul_score"].last()
        user_scores = np.sort(user_scores)
        curscore = cur["cumul_score"].values[0]
        if not user_scores:
            # by default assume the user is average
            percentile = 0.5
        else:
            if lower_better:
                percentile = len(user_scores[user_scores >= curscore]) / len(
                    user_scores
                )
            else:
                percentile = len(user_scores[user_scores <= curscore]) / len(
                    user_scores
                )
        assert 0 <= percentile <= 1
        cumul_rankings.append(percentile)
    forecasts["cumul_perc"] = np.array(cumul_rankings)
    return forecasts


# alternatively
# f.drop_duplicates(subset=['question_id', 'user_id', 'outcome', 'timestamp']).set_index('timestamp').groupby(['question_id', 'user_id', 'outcome']).resample('D').pad()


def frontfill(forecasts):
    """forecasts should be a dataframe with at least these five fields:
    question_id, user_id, timestamp, probability"""
    forecasts = forecasts.groupby(["question_id", "user_id", "answer_option"]).apply(
        _frontfill_group
    )
    forecasts.index = forecasts.index.droplevel(
        ["question_id", "user_id", "answer_option"]
    )
    return forecasts


def _frontfill_group(group):
    """warning: this makes the forecast ids useless"""
    dates = pd.date_range(
        start=min(group["timestamp"]),
        end=max(group["close_time"]),
        freq="D",
        normalize=True,
    )
    alldates = pd.DataFrame({"date": dates})
    group["date"] = group["timestamp"].apply(lambda x: x.round(freq="D"))
    group = group.merge(alldates, on="date", how="outer")
    group = group.sort_values(by="timestamp")
    group["timestamp"] = group["timestamp"].fillna(group["date"])
    group = group.fillna(method="ffill")
    group.drop(columns=["date"])
    return group


def generic_aggregate(
    group,
    summ="arith",
    format="probs",
    decay=1,
    extremize="noextr",
    extrfactor=3,
    fill=False,
):
    n = len(group)

    if n == 0:
        return

    if fill:
        group = frontfill(group)

    probabilities = group["probability"]

    if extremize == "befextr":
        p = probabilities
        probabilities = (p**extrfactor) / (
            ((p**extrfactor) + (1 - p)) ** (1 / extrfactor)
        )

    if decay != 1:
        if "NULL" in group["close_time"]:  # TODO: maybe not necessary anymore?
            weights = np.ones_like(probabilities)
        else:
            t_diffs = group["close_time"] - group["timestamp"]
            t_diffs = np.array([t.total_seconds() for t in t_diffs])
            weights = decay ** (t_diffs * 1 / 86400)
    else:
        weights = np.ones_like(probabilities)

    if format == "odds":
        probabilities = probabilities / (1 - probabilities)
    elif format == "logodds":
        probabilities = probabilities / (1 - probabilities)
        probabilities = np.log(probabilities)

    if summ == "arith":
        aggrval = np.sum(weights * probabilities) / np.sum(weights)
    elif summ == "geom":
        aggrval = statistics.geometric_mean(probabilities)
    elif summ == "median":
        aggrval = np.median(probabilities)

    if format == "odds":
        aggrval = aggrval / (1 + aggrval)
    elif format == "logodds":
        aggrval = np.exp(aggrval)
        aggrval = aggrval / (1 + aggrval)

    if extremize == "gjpextr":
        p = aggrval
        aggrval = (p**extrfactor) / (
            ((p**extrfactor) + (1 - p)) ** (1 / extrfactor)
        )
    elif extremize == "postextr":
        p = aggrval
        aggrval = p**extrfactor
    elif extremize == "neyextr":
        p = aggrval
        d = n * (math.sqrt(3 * n**2 - 3 * n + 1) - 2) / (n**2 - n - 1)
        aggrval = p*(d-1)

    return np.array([aggrval])

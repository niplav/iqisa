import re
import time
import random
import math
import statistics
import datetime as dt
import numpy as np
import pandas as pd

import iqisa as iqs

questions_files = ["{data_dir}/gjp/ifps.csv"]

processed_survey_files = ["{data_dir}/gjp/surveys.csv.zip"]

survey_files = [
    "{data_dir}/gjp/survey_fcasts.yr1.csv",
    "{data_dir}/gjp/survey_fcasts.yr2.csv",
    "{data_dir}/gjp/survey_fcasts.yr3.csv.zip",
    "{data_dir}/gjp/survey_fcasts.yr4.csv.zip",
]

processed_market_files = ["{data_dir}/gjp/markets.csv.zip"]

market_files = [
    "{data_dir}/gjp/pm_transactions.lum1.yr2.csv",
    "{data_dir}/gjp/pm_transactions.lum2.yr2.csv",
    "{data_dir}/gjp/pm_transactions.lum1.yr3.csv",
    "{data_dir}/gjp/pm_transactions.lum2a.yr3.csv",
    "{data_dir}/gjp/pm_transactions.lum2.yr3.csv",
    "{data_dir}/gjp/pm_transactions.inkling.yr3.csv",
    "{data_dir}/gjp/pm_transactions.control.yr4.csv",
    "{data_dir}/gjp/pm_transactions.batch.train.yr4.csv",
    "{data_dir}/gjp/pm_transactions.batch.notrain.yr4.csv",
    "{data_dir}/gjp/pm_transactions.supers.yr4.csv",
    "{data_dir}/gjp/pm_transactions.teams.yr4.csv",
]

_year2_default_changes = {
    "fixes": [
        "timestamp",
        "price_after_100",
        "question_id_str",
        "without_team_id",
        "insert_outcomes",
        "remove_voided",
        "conditional_options_a",
    ],
    "column_rename": {
        "IFPID": "question_id",
        "outcome": "answer_option",
        "user.ID": "user_id",
        "Op.Type": "op_type",
        "order.ID": "order_id",
        "buy": "isbuy",
        "long": "islong",
        "with.MM": "with_mm",
        "matching.order.ID": "matching_order_id",
        "price": "probability",
        "qty": "quantity",
        "by.agent": "by_agent",
    },
}

_year3_default_changes = {
    "fixes": [
        "timestamp",
        "price_before_100",
        "price_after_100",
        "prob_est_100",
        "question_id_str",
        "with_prob_est",
        "without_team_id",
        "insert_outcomes",
        "remove_voided",
        "conditional_options_a",
    ],
    "column_rename": {
        "IFPID": "question_id",
        "Outcome": "answer_option",
        "User.ID": "user_id",
        "Op.Type": "op_type",
        "Order.ID": "order_id",
        "isBuy": "isbuy",
        "isLong": "islong",
        "With.MM": "with_mm",
        "By.Agent": "by_agent",
        "Matching.Order.ID": "matching_order_id",
        "Order.Price": "probability",
        "Order.Qty": "quantity",
        "Trade.Price": "prob_before_trade",
        "Trade.Qty": "trade_qty",
        "Tru.Belief": "prob_est",
        "Low.Fuse": "low_fuse",
        "Max.Bid": "max_bid",
        "Min.Ask": "min_ask",
        "High.Fuse": "high_fuse",
        "Min.Qty": "min_qty",
        "Divest.Only": "divest_only",
    },
}

_year4_default_changes = {
    "fixes": [
        "timestamp",
        "created_date_us",
        "price_before_perc",
        "price_after_perc",
        "prob_est_perc",
        "question_id_str",
        "id_in_name",
        "insert_outcomes",
        "option_from_stock_name",
        "with_prob_est",
        "without_team_id",
        "with_before_trade",
    ],
    "column_rename": {
        "Trade.ID": "order_id",
        "Market.Name": "market_name",
        "Stock.Name": "stock_name",
        "Trade.Type": "trade_type",
        "Quantity": "quantity",
        "Spent": "spent",
        "Created.At": "created_at",
        "Filled.At": "timestamp",
        "Price.Before": "prob_before_trade",
        "Price.After": "probability",
        "Probability.Estimate": "prob_est",
        "GJP.User.ID": "user_id",
    },
}

_market_fixes = {
    "./data/gjp/pm_transactions.lum1.yr2.csv": _year2_default_changes,
    "./data/gjp/pm_transactions.lum2.yr2.csv": _year2_default_changes,
    "./data/gjp/pm_transactions.lum1.yr3.csv": _year3_default_changes,
    "./data/gjp/pm_transactions.lum2a.yr3.csv": _year3_default_changes,
    "./data/gjp/pm_transactions.lum2.yr3.csv": {
        "fixes": [
            "timestamp",
            "price_after_100",
            "prob_est_100",
            "question_id_str",
            "team_bad",
            "with_before_trade",
            "insert_outcomes",
            "with_prob_est",
            "remove_voided",
            "conditional_options_a",
        ],
        "column_rename": {
            "IFPID": "question_id",
            "Outcome": "answer_option",
            "User.ID": "user_id",
            "Team": "team_id",
            "Op.Type": "op_type",
            "Order.ID": "order_id",
            "isBuy": "isbuy",
            "isLong": "islong",
            "With.MM": "with_mm",
            "By.Agent": "by_agent",
            "Matching.Order.ID": "matching_order_id",
            "Order.Price": "probability",
            "Order.Qty": "quantity",
            "Trade.Price": "prob_before_trade",
            "Trade.Qty": "trade_qty",
            "Tru.Belief": "prob_est",
            "Low.Fuse": "low_fuse",
            "Max.Bid": "max_bid",
            "Min.Ask": "min_ask",
            "High.Fuse": "high_fuse",
            "Min.Qty": "min_qty",
            "Divest.Only": "divest_only",
        },
    },
    "./data/gjp/pm_transactions.inkling.yr3.csv": {
        "fixes": [
            "timestamp",
            "created_date_us",
            "price_before_perc",
            "price_after_perc",
            "prob_est_perc",
            "id_by_name",
            "option_from_stock_name",
            "with_before_trade",
            "with_prob_est",
            "without_team_id",
            "insert_outcomes",
            "remove_voided",
            "conditional_options_a",
        ],
        "column_rename": {
            "trade.id": "order_id",
            "market.name": "market_name",
            "stock.name": "stock_name",
            "type": "op_type",
            "created.at": "created_at",
            "filled.at": "timestamp",
            "price_before": "prob_before_trade",
            "price_after": "probability",
            "probability_estimate": "prob_est",
            "gjp.user.id": "user_id",
        },
    },
    "./data/gjp/pm_transactions.teams.yr4.csv": {
        "fixes": [
            "timestamp",
            "created_date_us",
            "price_before_perc",
            "price_after_perc",
            "prob_est_perc",
            "question_id_str",
            "id_in_name",
            "insert_outcome",
            "option_from_stock_name",
            "with_before_trade",
            "with_prob_est",
            "insert_outcomes",
        ],
        "column_rename": {
            "Trade.ID": "order_id",
            "Market.Name": "market_name",
            "Stock.Name": "stock_name",
            "Trade.Type": "trade_type",
            "Quantity": "quantity",
            "Spent": "spent",
            "Created.At": "created_at",
            "Filled.At": "timestamp",
            "Price.Before": "prob_before_trade",
            "Price.After": "probability",
            "Probability.Estimate": "prob_est",
            "GJP.Team.ID": "team_id",
            "GJP.User.ID": "user_id",
        },
    },
    "./data/gjp/pm_transactions.batch.train.yr4.csv": _year4_default_changes,
    "./data/gjp/pm_transactions.batch.notrain.yr4.csv": _year4_default_changes,
    "./data/gjp/pm_transactions.control.yr4.csv": _year4_default_changes,
    "./data/gjp/pm_transactions.batch.notrain.yr4.csv": _year4_default_changes,
    "./data/gjp/pm_transactions.supers.yr4.csv": _year4_default_changes,
}


def _simplify_id(question_id):
    pattern = re.compile("^[0-9]+")
    return (
        pattern.findall(question_id)[0] if isinstance(question_id, str) else question_id
    )


def _extract_id(market_name):
    pattern = re.compile("^[0-9]+")
    return str(pattern.findall(market_name)[0])


def _extract_type(question_id):
    pattern = re.compile("-([0-6])$")
    return int(pattern.findall(question_id)[0])


def _extract_team(team_id):
    if team_id == "DEFAULT":
        return 0  # team ID 0 has not been given.
    pattern = re.compile("e([0-9]{1,2})$")
    return int(pattern.findall(team_id)[0])


# the data has trades on markets, stock names (sn) are possibly substrings
# of the options, preceded by the name of the option [a-e].
# yeah, i don'stockname_and_options know why anyone would do this either.
def _get_option_from_options(stockname_and_options):
    option = stockname_and_options[1]
    stockname = stockname_and_options[0]
    # for some reason (!?) the answer options may contain these
    stockname = re.escape(stockname.replace("**", ""))
    option = option.replace("**", "")
    pattern = re.compile("\((.)\) ?" + stockname)
    finds = pattern.findall(option)
    if finds:
        return finds[0]
    # the conditional came to pass
    pattern = re.compile(stockname + "[^\(]+\((.)\)")
    finds = pattern.findall(option)
    if finds:
        return finds[0]
    # the conditional didn'stockname_and_options come to pass
    pattern = re.compile("\((.)\)[^\(]+$")
    finds = pattern.findall(option)
    if finds:
        return finds[0]
    return (
        ""  # give up, but this doesn'stockname_and_options happen on the current data
    )


def load_questions(files=None, data_dir: str = "./data"):
    if files is None:
        files = questions_files
        files = [x.format(data_dir=data_dir) for x in files]
    questions = pd.DataFrame()

    for f in files:
        questions = pd.concat([questions, pd.read_csv(f)])

    date_fields = ["date_start", "date_suspend", "date_to_close", "date_closed"]

    for f in date_fields:
        questions[f] = pd.to_datetime(questions[f], dayfirst=True)

    questions = questions.rename(
        columns={
            "ifp_id": "question_id",
            "date_start": "open_time",
            "date_suspend": "close_time",
            "date_to_close": "resolve_time",
            "date_closed": "close_date",
            "days_open": "time_open",
            "q_text": "q_title",
        },
        errors="raise",
    )
    questions.loc[:, "question_id"] = questions["question_id"].map(_simplify_id)
    questions["question_id"] = pd.to_numeric(questions["question_id"], downcast="float")
    questions["time_open"] = pd.to_timedelta(questions["time_open"], unit="D")

    return questions


def _load_complete_markets(files=None, probmargin=0.005):
    if files is None:
        files = market_files

    forecasts = pd.DataFrame()

    questions = load_questions()
    questions = questions.loc[questions["q_status"] != "voided"]
    voidedquestions = questions.loc[questions["q_status"] == "voided"][
        ["q_type", "question_id"]
    ]

    for f in files:
        market = pd.read_csv(f)
        market = market.rename(
            columns=_market_fixes[f]["column_rename"], errors="raise"
        )

        # We want to use question_id below, but we want it to
        # have the correct type already, so sometimes we have to
        # generate it from other data.
        if "id_by_name" in _market_fixes[f]["fixes"]:
            q_titles = questions[["question_id", "q_title"]]
            market = pd.merge(
                market, q_titles, left_on="market_name", right_on="q_title", how="inner"
            )
            market.pop("q_title")
        if "id_in_name" in _market_fixes[f]["fixes"]:
            market["question_id"] = market["market_name"].map(_extract_id)

        market["question_id"] = pd.to_numeric(market["question_id"])

        if "created_date_us" in _market_fixes[f]["fixes"]:
            market["created_at"] = pd.to_datetime(market["created_at"], dayfirst=True)
        if "timestamp" in _market_fixes[f]["fixes"]:
            market["timestamp"] = pd.to_datetime(market["timestamp"], dayfirst=True)
        if "price_after_perc" in _market_fixes[f]["fixes"]:
            market["probability"] = market["probability"].map(
                lambda x: float(x.replace("%", "")) / 100
            )
        if "price_before_perc" in _market_fixes[f]["fixes"]:
            market["prob_before_trade"] = market["prob_before_trade"].map(
                lambda x: float(x.replace("%", "")) / 100
            )
        if "prob_est_perc" in _market_fixes[f]["fixes"]:
            strperc = market.loc[market["prob_est"].map(lambda x: isinstance(x, str))]
            market.loc[
                market["prob_est"].map(lambda x: isinstance(x, str)), "prob_est"
            ] = strperc["prob_est"].map(
                lambda x: np.nan if x == "no" else float(x.replace("%", "")) / 100
            )
        if "price_after_100" in _market_fixes[f]["fixes"]:
            market["probability"] = market["probability"].map(lambda x: float(x)) / 100
        if "price_before_100" in _market_fixes[f]["fixes"]:
            market["prob_before_trade"] = (
                market["prob_before_trade"].map(lambda x: float(x)) / 100
            )
        if "prob_est_100" in _market_fixes[f]["fixes"]:
            market["prob_est"] = market["prob_est"].map(lambda x: float(x)) / 100
        if "insert_outcomes" in _market_fixes[f]["fixes"]:
            q_outcomes = questions[["question_id", "outcome"]]
            market = pd.merge(market, q_outcomes, on="question_id", how="inner")
        if "option_from_stock_name" in _market_fixes[f]["fixes"]:
            q_options = questions[["question_id", "options"]]
            with_options = pd.merge(market, q_options, on="question_id", how="inner")
            market["answer_option"] = with_options[["stock_name", "options"]].apply(
                _get_option_from_options, axis=1
            )
        if "team_bad" in _market_fixes[f]["fixes"]:
            market["team_id"] = market["team_id"].apply(_extract_team)
        if "with_before_trade" in _market_fixes[f]["fixes"]:
            market.loc[
                market["prob_before_trade"] <= 0, "prob_before_trade"
            ] = probmargin
            market.loc[market["prob_before_trade"] >= 1, "prob_before_trade"] = (
                1 - probmargin
            )
        if "with_prob_est" in _market_fixes[f]["fixes"]:
            market.loc[market["prob_est"] <= 0, "prob_est"] = probmargin
            market.loc[market["prob_est"] >= 1, "prob_est"] = 1 - probmargin
        if "without_team_id" in _market_fixes[f]["fixes"]:
            market = market.assign(team_id=0)
        # On conditional markets, the answer option refers to the branch
        # of the conditional market ('a' is the first market
        # (-1), 'b' is the second market (-2), etc. Don't
        # ask, I didn't make this up). Therefore, we here
        # have to remove forecasts on voided questions
        # from the dataset. Furthermore, the answer on
        # the non-voided conditional market is always
        # assumed to be "a", so we have to insert it.
        if "remove_voided" in _market_fixes[f]["fixes"]:
            # We assume that the answer_option designates the branch
            market["q_type"] = market["answer_option"].apply(
                lambda x: x.encode()[0] - ("a".encode()[0] - 1)
            )
            # We remove the forecasts on voided questions
            # from the dataset by first outer joining the forecasts
            # and the voided questions, and then removing
            # rows where both occurred.
            market = pd.merge(
                market,
                voidedquestions,
                on=["q_type", "question_id"],
                how="outer",
                indicator=True,
            )
            market = market[
                ~((market["_merge"] == "both") | (market["_merge"] == "right_only"))
            ].drop("_merge", axis=1)
            market = market.drop(["q_type"], axis=1)
        # Since the field 'answer_option' on conditional prediction markets
        # refers to the branch of the market (as per personal communication from
        # the GJOpen team), the default answer for prices
        # on conditional markets in 'a'. We have to set
        # this here.
        if "conditional_options_a" in _market_fixes[f]["fixes"]:
            onlytype = questions[["question_id", "q_type"]]
            # this works because the question_ids
            # of onlytype are a superset of the
            # question_ids of questions.
            market = pd.merge(market, onlytype, on=["question_id"], how="inner")
            market.loc[
                (market["q_type"] != 0) & (market["q_type"] != 6), "answer_option"
            ] = "a"
            market = market.drop(["q_type"], axis=1)

        assert len(market) > 0

        forecasts = pd.concat([forecasts, market], join="outer")

    # add the some question-specific information to the trades
    qdata = questions.loc[questions["question_id"].isin(forecasts["question_id"])][
        [
            "question_id",
            "open_time",
            "close_time",
            "resolve_time",
            "time_open",
            "n_opts",
            "options",
            "q_status",
            "q_type",
        ]
    ]

    forecasts = pd.merge(forecasts, qdata, on="question_id", how="inner")

    # prices in (-∞,0]∪[1,∞) are truncated to [MIN_PROB, 1-MIN_PROB]
    forecasts.loc[forecasts["probability"] <= 0, "probability"] = probmargin
    forecasts.loc[forecasts["probability"] >= 1, "probability"] = 1 - probmargin
    forecasts.loc[forecasts["q_status"] == "closed", "q_status"] = "resolved"

    forecasts["user_id"] = pd.to_numeric(forecasts["user_id"], downcast="float")
    forecasts["team_id"] = pd.to_numeric(forecasts["team_id"], downcast="float")

    return forecasts


def _load_complete_surveys(files=None, probmargin=0.005):
    if files is None:
        files = survey_files

    forecasts = pd.DataFrame()

    for f in files:
        forecasts = pd.concat([forecasts, pd.read_csv(f)])

    forecasts["timestamp"] = pd.to_datetime(forecasts["timestamp"])
    forecasts["fcast_date"] = pd.to_datetime(forecasts["fcast_date"])

    forecasts = forecasts.rename(
        columns={
            "ifp_id": "question_id",
            "value": "probability",
            "team": "team_id",
            "ctt": "user_type",
        },
        errors="raise",
    )
    forecasts["q_type"] = forecasts["question_id"].apply(_extract_type)
    forecasts["question_id"] = forecasts["question_id"].apply(_extract_id)
    forecasts["question_id"] = pd.to_numeric(forecasts["question_id"], downcast="float")

    questions = load_questions()

    forecasts = pd.merge(
        forecasts, questions, on=["question_id", "q_type"], suffixes=(None, "_x")
    )

    forecasts.pop("q_status_x")

    forecasts.loc[forecasts["probability"] == 0, "probability"] = probmargin
    forecasts.loc[forecasts["probability"] == 1, "probability"] = 1 - probmargin

    forecasts["user_id"] = pd.to_numeric(forecasts["user_id"])
    forecasts["team_id"] = pd.to_numeric(forecasts["team_id"])

    forecasts.loc[forecasts["q_status"] == "closed", "q_status"] = "resolved"

    return forecasts


def load_surveys(files=None, processed=True, complete=False, data_dir: str = "./data"):
    if processed and complete:
        raise Exception("Can't load complete data from a processed file.")
    if files is None:
        if processed:
            files = processed_survey_files
        else:
            files = survey_files

        files = [x.format(data_dir=data_dir) for x in files]

    if processed:
        return _load_processed(files)
    if complete:
        return _load_complete_surveys(files)

    forecasts = _load_complete_surveys(files)
    forecasts = forecasts.reindex(columns=iqs.comparable_index)

    return forecasts


def load_markets(files=None, processed=True, complete=False, data_dir: str = "./data"):
    if processed and complete:
        raise Exception("Can't load complete data from a processed file.")
    if files is None:
        if processed:
            files = processed_market_files
        else:
            files = market_files

        files = [x.format(data_dir=data_dir) for x in files]

    if processed:
        return _load_processed(files)
    if complete:
        return _load_complete_markets(files)

    forecasts = _load_complete_markets(files)
    forecasts = forecasts.reindex(columns=iqs.comparable_index)

    return forecasts


def _load_processed(files):
    forecasts = pd.DataFrame()

    for f in files:
        forecasts = pd.concat([forecasts, pd.read_csv(f)])

    date_fields = ["timestamp", "open_time", "close_time", "resolve_time"]

    for f in date_fields:
        forecasts[f] = pd.to_datetime(forecasts[f], dayfirst=True)

    forecasts["time_open"] = pd.to_timedelta(forecasts["time_open"])
    return forecasts

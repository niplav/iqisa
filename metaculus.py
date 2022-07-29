import json

import datetime as dt
import numpy as np
import pandas as pd

import iqisa as iqs

questions_files = ["./data/metaculus/questions.json"]


def load_private_binary(data_file):
    forecasts = _load_complete_private_binary(data_file)
    return forecasts


def _load_complete_private_binary(data_file):
    f = open(data_file)
    jsondata = json.load(f)

    user_ids = []
    team_ids = []
    probabilities = []
    answer_options = []
    timestamps = []
    outcomes = []
    open_times = []
    resolve_times = []
    question_titles = []

    for question in jsondata:
        if question["question_type"] == "binary":
            resolution = str(question["resolution"])
            open_time = dt.datetime.fromisoformat(question["publish_time"])
            open_time = dt.datetime.fromisoformat(question["publish_time"])
            resolve_time = dt.datetime.fromisoformat(question["resolve_time"])
            question_title = str(question["question_title"])
            numf = 0
            for forecast in question["prediction_timeseries"]:
                user_ids.append(int(forecast["user_id"]))
                probabilities.append(float(forecast["prediction"]))
                timestamps.append(dt.datetime.fromtimestamp(forecast["timestamp"]))
                numf += 1
            open_times += [open_time] * numf
            resolve_times += [resolve_time] * numf
            outcomes += [resolution] * numf
            question_titles += [question_title] * numf
    numf = len(probabilities)
    answer_options = ["1"] * numf
    outcomes = ["1"] * numf
    team_ids = [0] * numf
    n_opts = [2] * numf
    options = ["(0) No, (1) Yes"] * numf
    q_status = ["resolved"] * numf
    q_type = [0] * numf

    forecasts = pd.DataFrame(
        {
            "user_id": user_ids,
            "team_id": team_ids,
            "probability": probabilities,
            "answer_option": answer_options,
            "timestamp": timestamps,
            "outcome": outcomes,
            "open_time": open_times,
            "resolve_time": resolve_times,
            "n_opts": n_opts,
            "options": options,
            "q_status": q_status,
            "q_type": q_type,
            "q_title": question_titles,
        }
    )

    questions = load_questions()
    forecasts = pd.merge(forecasts, questions, on=["q_title"], suffixes=("", "_y"))
    forecasts = forecasts.drop(
        columns=["open_time_y", "resolve_time_y", "outcome_y", "q_status_y"]
    )
    forecasts.reindex(
        columns=[
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
            "days_open",
            "n_opts",
            "options",
            "q_status",
            "q_type",
        ]
    )

    forecasts["question_id"] = pd.to_numeric(forecasts["question_id"], downcast="float")
    forecasts["user_id"] = pd.to_numeric(forecasts["user_id"], downcast="float")
    forecasts["team_id"] = pd.to_numeric(forecasts["team_id"], downcast="float")
    forecasts["question_id"] = pd.to_numeric(forecasts["question_id"], downcast="float")

    return forecasts


def load_questions(files=None):
    if files is None:
        files = questions_files

    questions = pd.DataFrame()

    for data_file in files:
        f = open(data_file)
        jsondata = json.load(f)

        question_ids = []
        open_times = []
        close_times = []
        resolve_times = []
        outcomes = []
        question_titles = []
        question_statuses = []

        for question in jsondata:
            question_ids.append(int(question["question_id"]))
            # apparently datetime.fromisoformat doesn't
            # recognize the postfix 'Z' as indicating UTC as
            # a timezone (why? why? why?), so I'll remove it
            # here, since all times are UTC anyway.
            open_time = dt.datetime.fromisoformat(
                question["open_time"].replace("Z", "")
            )
            open_times.append(open_time)
            close_time = dt.datetime.fromisoformat(
                question["close_time"].replace("Z", "")
            )
            close_times.append(close_time)
            resolve_time = dt.datetime.fromisoformat(
                question["resolve_time"].replace("Z", "")
            )
            resolve_times.append(resolve_time)
            if question["outcome"] is None or question["outcome"] == -1:
                outcomes.append(np.nan)
            else:
                outcomes.append(str(question["outcome"]))
            question_titles.append(question["question_title"])

            if question["outcome"] is None:
                # I don't see the data giving any better indication of
                # whether the question has closed
                # TODO: think about this with a Yoda timer?
                now = dt.datetime.utcnow()
                if now > close_time:
                    question_statuses.append("closed")
                else:
                    question_statuses.append("open")
            elif question["outcome"] == -1:
                question_statuses.append("voided")
            else:
                question_statuses.append("resolved")

        numq = len(question_ids)
        n_opts = [2] * numq
        q_type = [0] * numq
        options = ["(0) No, (1) Yes"] * numq
        days_open = np.array(close_times) - np.array(open_times)

        newquestions = pd.DataFrame(
            {
                "question_id": question_ids,
                "q_title": question_titles,
                "q_status": question_statuses,
                "open_time": open_times,
                "close_time": close_times,
                "resolve_time": resolve_times,
                "outcome": outcomes,
                "days_open": days_open,
                "n_opts": n_opts,
                "options": options,
            }
        )

        questions = pd.concat([questions, newquestions])

    return questions

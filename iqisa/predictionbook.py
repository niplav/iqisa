import sys
import time
import zipfile
import pandas as pd

import datetime as dt

from bs4 import BeautifulSoup

public_raw_files = ["{data_dir}/predictionbook/public_raw.zip"]
public_files = ["{data_dir}/predictionbook/public.csv.zip"]
question_file = ["{data_dir}/predictionbook/questions.csv.zip"]


def load(files=None, processed=True, data_dir: str = "./data"):
    if files is None:
        if processed:
            files = public_files
        else:
            files = public_raw_files

        files = [x.format(data_dir=data_dir) for x in files]

    if processed:
        return _load_processed(files)
    return _load_complete(files)


def _load_processed(files):
    forecasts = pd.DataFrame()

    for f in files:
        forecasts = pd.concat([forecasts, pd.read_csv(f)])

    date_fields = ["timestamp", "open_time", "close_time", "resolve_time"]

    for f in date_fields:
        forecasts[f] = pd.to_datetime(forecasts[f], errors="coerce", dayfirst=True)

    # TODO: fix this. datetime representation is in nanoseconds and this can overflow.
    # forecasts["time_open"] = pd.to_timedelta(forecasts["time_open"], errors="coerce")

    return forecasts


def _load_complete(data_file):
    forecasts = pd.DataFrame()

    zf = zipfile.ZipFile(data_file)
    for filename in zf.namelist():
        f = zf.open(filename)
        content = f.read()
        question_forecasts = _get_forecast_data(content, filename)
        forecasts = pd.concat([forecasts, question_forecasts])
        f.close()

    zf.close()

    return forecasts


def _get_forecast_data(content, filename):
    parsed_content = BeautifulSoup(content, "html.parser")

    probabilities = []
    user_ids = []
    timestamps = []

    question_id = filename.strip(".html")
    timedata = parsed_content.find(
        lambda tag: tag.name == "p" and "Created by" in tag.text
    )
    opened = timedata.find("span", class_="date").get("title")
    open_time = pd.to_datetime(opened)
    # we do this whole annoying dance *because* native pandas datetime works in
    # nanoseconds, and some resolution datetimes are way too big for that.
    # usually I'd just use dt.datetime.fromisoformat() here and let it do the
    # annoying stuff, but since this is non ISO-8601-formatted, I have to do it
    # manually.
    closed = timedata.find_all("span", class_="date")[1].get("title")
    close_time = time.strptime(closed, "%Y-%m-%d %H:%M:%S UTC")
    close_time = dt.datetime.fromtimestamp(time.mktime(close_time), tz=dt.timezone.utc)

    if timedata.find_all("span", class_="judgement") == []:
        outcome = None
        resolve_time = None
        q_status = "open"
    else:
        outcome = timedata.find("span", class_="outcome").string
        q_status = "resolved"
        if outcome == "right":
            outcome = 1.0
        elif outcome == "wrong":
            outcome = 0.0
        elif outcome == "unknown":
            q_status = "ambiguous"
            outcome = -1.0
        else:
            outcome = None
        resolved = timedata.find("span", class_="date created_at").get("title")
        resolve_time = pd.to_datetime(resolved)

    responses = parsed_content.find_all("li", class_="response")

    for r in responses:
        forecasts = r.find_all("span", class_="confidence")
        if forecasts != []:
            probability = (
                float(r.find_all("span", class_="confidence")[0].text.strip("%")) / 100
            )
        else:
            continue
        probabilities.append(probability)
        user_id = r.find("a", class_="user").string
        user_ids.append(user_id)
        estimated = r.find("span", class_="date").get("title")
        timestamp = pd.to_datetime(estimated)
        timestamps.append(timestamp)

    numf = len(probabilities)

    question_ids = [question_id] * numf

    open_times = [open_time] * numf
    close_times = [close_time] * numf
    resolve_times = [resolve_time] * numf
    time_open = [close_time - open_time] * numf

    outcomes = [outcome] * numf

    answer_options = ["1"] * numf
    team_ids = [0] * numf
    n_opts = [2] * numf
    options = ["(0) No, (1) Yes, (-1) Ambiguous, (None) Still open"] * numf
    q_type = [0] * numf

    forecasts = pd.DataFrame(
        {
            "question_id": question_ids,
            "user_id": user_ids,
            "team_id": team_ids,
            "probability": probabilities,
            "answer_option": answer_options,
            "timestamp": timestamps,
            "outcome": outcomes,
            "open_time": open_times,
            "close_time": close_times,
            "resolve_time": resolve_times,
            "time_open": time_open,
            "n_opts": n_opts,
            "options": options,
            "q_status": q_status,
            "q_type": q_type,
        }
    )

    return forecasts


def load_questions(files=None, processed=True, data_dir: str = "./data"):
    if files is None:
        if processed:
            files = question_file[0]
        else:
            files = public_raw_files[0]  # not sure here, didn't get it to work

        files = files.format(data_dir=data_dir)

    if processed:
        return pd.read_csv(files)

    questions = pd.DataFrame()

    zf = zipfile.ZipFile(files)
    for filename in zf.namelist():
        f = zf.open(filename)
        content = f.read()
        question_data = _get_questions_data(content, filename)
        questions = pd.concat([questions, question_data])
        f.close()

    zf.close()

    return questions


def _get_questions_data(content, filename):
    print(filename)
    parsed_content = BeautifulSoup(content, "html.parser")

    question_id = filename.strip(".html")
    title_elem = parsed_content.find("h1")
    if title_elem is None:
        q_title = None
    else:
        q_title = title_elem.get_text(strip=True).strip()
    timedata = parsed_content.find(
        lambda tag: tag.name == "p" and "Created by" in tag.text
    )
    opened = timedata.find("span", class_="date").get("title")
    open_time = pd.to_datetime(opened)
    # same as in the forecast loading function
    closed = timedata.find_all("span", class_="date")[1].get("title")
    close_time = time.strptime(closed, "%Y-%m-%d %H:%M:%S UTC")
    close_time = dt.datetime.fromtimestamp(time.mktime(close_time), tz=dt.timezone.utc)

    if timedata.find_all("span", class_="judgement") == []:
        outcome = None
        resolve_time = None
        q_status = "open"
    else:
        outcome = timedata.find("span", class_="outcome").string
        q_status = "resolved"
        if outcome == "right":
            outcome = 1.0
        elif outcome == "wrong":
            outcome = 0.0
        elif outcome == "unknown":
            q_status = "ambiguous"
            outcome = -1.0
        else:
            outcome = None
        resolved = timedata.find("span", class_="date created_at").get("title")
        resolve_time = pd.to_datetime(resolved)

    time_open = close_time - open_time

    n_opts = 2
    options = "(0) No, (1) Yes, (-1) Ambiguous, (None) Still open"

    question_data = pd.DataFrame(
        {
            "question_id": [question_id],
            "q_title": [q_title],
            "q_status": [q_status],
            "open_time": [open_time],
            "close_time": [close_time],
            "resolve_time": [resolve_time],
            "outcome": [outcome],
            "time_open": [time_open],
            "n_opts": [n_opts],
            "options": [options],
        }
    )

    return question_data

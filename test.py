import numpy as np
import pandas as pd

import gjp

m = gjp.load_markets()
s = gjp.load_surveys()

# Test the presence of some rows in the market files

assert (
    len(
        m.loc[
            (m["question_id"] == 1040)
            & (m["answer_option"] == "a")
            & (m["user_id"] == 6203)
            & (m["probability"] == 0.45)
        ]
    )
    == 1
)

assert (
    len(
        m.loc[
            (m["user_id"] == 3246)
            & (m["probability"] == 0.3725)
            & (m["answer_option"] == "b")
        ]
    )
    == 1
)

assert (
    len(
        m.loc[
            (m["answer_option"] == "a")
            & (m["user_id"] == 6093)
            & (m["question_id"] == 1291)
            & (m["timestamp"] == pd.to_datetime("2013-11-07T16:02:36"))
            & (m["probability"] == 0.28)
        ]
    )
    == 1
)

assert (
    len(
        m.loc[
            (m["user_id"] == 15864)
            & (m["probability"] == 0.7859)
            & (m["timestamp"] == pd.to_datetime("2015-01-04T08:12"))
        ]
    )
    == 1
)

assert (
    len(
        m.loc[
            (m["probability"] == 0.1726)
            & (m["user_id"] == 8545)
            & (m["question_id"] == 1541)
            & (m["answer_option"] == "a")
        ]
    )
    == 1
)

assert len(m.loc[(m["timestamp"] == pd.to_datetime("2015-09-06T17:07"))]) == 1

assert (
    len(
        m.loc[
            (m["timestamp"] == pd.to_datetime("2015-02-17T19:36"))
            & (m["probability"] == 0.6074)
        ]
    )
    == 1
)

assert (
    len(
        m.loc[
            (m["user_id"] == 6707)
            & (m["question_id"] == 1240)
            & (m["probability"] == 0.05)
            & (m["timestamp"] == pd.to_datetime("2013-08-05T06:23:49"))
        ]
    )
    == 1
)

assert (
    len(
        s.loc[
            (s["user_id"] == 5723)
            & (s["team_id"] == 3)
            & (s["probability"] == 0.35)
            & (s["q_type"] == 6)
            & (s["answer_option"] == "b")
            & (s["question_id"] == 1126)
        ]
    )
    == 1
)

assert np.all(m.columns == s.columns)

Iqisa Documentation
======================

Data Structures
----------------

### Comparable Forecast Data General Structure

The data returned by any function that loads data from a file with
forecasts or prices from a prediction market, in the format of a pandas
DataFrame. The data for prediction markets and survey forecasts is
slightly different, but they share many fields, which are described here.

Those fields are:

<!--TODO: make this a table-->

* `question_id`: The unique ID of the question, type `int64`. Follows the format `[0-9]{4}`.
* `user_id`: The unique ID of the user who made the forecast, type `int`.
* `team_id`: The ID of the team the user was in, type `int64`. The team "DEFAULT" was given the ID 0.
* `probability`: The probability assigned in the forecast, type `float64`. Probabilities (or probabilities implied by market prices) ≥1 were changed to 0.995, and ≤0 to 0.005.
* `answer_option`: The answer option selected by the user, type `str`. One of 'a', 'b', 'c', 'd' or 'e' (or rarely `np.nan` for market data).
* `timestamp`: The time at which the forecast/trade was made, type `datetime64[ns]`.
* `outcome`: The outcome of the question, type `str`. One of 'a', 'b', 'c', 'd', or 'e' (or rarely `np.nan`, in the case of voided questions).
* `date_start`: The date at which the question was opened, i.e. at which forecasts could start. Type `datetime64[ns]`
* `date_suspend`: The datetime at which the question was suspended, i.e. at which no further forecasts were possible. Type `datetime64[ns]`. The biggest difference from `date_closed` seems to be that it also includes the time of closures.
* `date_to_close`: The planned closing date of the question, type `datetime64[ns]`.
* `date_closed`: The datetime at which the question was closed, type `datetime64[ns]`.
* `days_open`: The days for which the quesion was open, type `float64`.
* `n_opts`: The number of options the question had, type `int64`.
* `options`: A string containing a description of the different possible options, type `str`.
* `q_status`: The status of the question the forecast was made on, type `str`. One of 'closed', 'voided' or 'active'.
* `q_type`: The type of the question, type `int64`. Integer between 0 and 6 (inclusive).
	* 0: regular binomial or multinomial question
	* 1-5: conditional question, index designated by the specific type (`q_type` 2: 2nd conditional question)
	* 6: Ordered multinomial question

### `survey_files`

A list containing the names of all files in the dataset that contain
data from surveys.

### `market_files`

A list containing the names of all files in the dataset that contain
trades on prediction markets.

Functions
----------

### `get_comparable_survey_forecasts(files)`

Reads & returns a datastructure containing all forecasts reported by
forecasters in surveys (that is, all forecasts not made on a prediction
market), with columns selected so they are shared with every other
dataset.

#### Arguments

* `files`: a list of strings, all containing the names of files containing data from survey forecasts.

#### Returns

A pandas DataFrame of the of the format described
[here](#Comparable-Forecast-Data-General-Structure).

#### Example

Load the data from all files containing survey data:

	survey_forecasts=get_comparable_survey_forecasts(survey_files)

### `get_comparable_market_forecasts(files)`

Reads & returns a datastructure containing all forecasts that can be
computed from the prices on the prediction markets collected in the
files in `files`, with fields selected so that they are shared by every
other dataset.

#### Arguments

* `files`: a list of strings, all names of files containing data from prediction market data.

#### Returns

A pandas DataFrame of the of the format described
[here](#Comparable-Forecast-Data-General-Structure).

#### Example

Load the data from all files containing survey data:

	market_forecasts=get_comparable_market_forecasts(market_files)

### `get_survey_forecasts(files)`

Reads & returns a datastructure containing all forecasts reported by
forecasters in surveys, with all fields in the original CSV.

#### Arguments

* `files`: a list of strings, all containing the names of files containing data from survey forecasts, from which the resulting data will be read.

### Returns

A pandas DataFrame that is a superframe (additional
columns, but no additional rows) of the frame returned by
[`get_comparable_survey_forecasts`](#getcomparablesurveyforecastsfiles).
Additional columns it contains:

* `forecast_id`
* `fcast_type`
* `fcast_date`
* `expertise`
* `viewtime`
* `year`
* `q_text`
* `q_desc`
* `short_title`

### `get_market_forecasts(files)`

Reads & returns a datastructure containing all forecasts implied by
prices on prediction markets, with all columns in the original dataset.

#### Arguments

* `files`: a list of strings, all containing the names of files containing data from markets, from which the resulting data will be read.

### Returns

A pandas DataFrame that is a superframe (additional
columns, but no additional rows) of the frame returned by
[`get_comparable_market_forecasts`](#getcomparablemarketforecastsfiles).
Additional columns it contains:

* `islong`
* `by_agent`
* `op_type`
* `spent`
* `min_qty`
* `trade_type`
* `with_mm`
* `divest_only`
* `prob_after_trade`
* `matching_order_id`
* `high_fuse`
* `stock_name`
* `low_fuse`
* `created_at`
* `filled_at`
* `trade_qty`
* `isbuy`
* `prob_est`
* `market_name`
* `quantity`
* `min_ask`
* `experience`
* `max_bid`
* `order_id`

### `frontfill_forecasts(forecasts)`

__Warning__: This function makes the dataset given to it ~100 times
bigger, which might lead to running of out RAM.

Return a set of forecasts so that forecasts by individual forecasters are
repeated daily until they make a new forecast or the question is closed.

This function returns a new DataFrame and doesn't change the DataFrame
given as an argument.

#### Arguments

A DataFrame of the format described [here](#Comparable-Forecast-Data-General-Structure).

Specifically, the DataFrame should have the following columns:

* `question_id`
* `user_id`
* `answer_option`
* `fcast_date`
* `timestamp`

#### Returns

A DataFrame of the format described [here](#Comparable-Forecast-Data-General-Structure).

#### Example

	$ python3 -i gjplib.py
	>>> survey_files=['./data/survey_fcasts_mini.yr1.csv']
	>>> survey_forecasts=get_survey_forecasts()
	>>> len(survey_forecasts)
	9999
	>>> survey_forecasts=frontfill_forecasts(survey_forecasts)
	>>> len(survey_forecasts)
	1086926

### `aggregate(forecasts, aggregation_function, *args)`

Aggregate and score predictions on questions, methods can be given by
the user.

This function returns a new DataFrame with the aggregated data.

#### Arguments

The type signature of the function is

	aggregate: Dataframe × (DataFrame × Optional(arguments) -> [0,1]) × Optional(arguments) -> DataFrame

To elaborate a bit further:

* First argument (`forecasts`): A DataFrame of the format described [here](#Comparable-Forecast-Data-General-Structure), needs the following columns:
	* `question_id`
	* `timestamp`
	* `probability`
	* `answer_option`
	* `outcome`
* Second argument (`aggregation_function`): The user-defined aggregation function, which is called for on each set of forecasts made on the same question for the same answer option.
	* Receives:
		* A DataFrame that is a subset of rows of `forecasts` (all with the same `question_id`)
		* Optional arguments passed on by `aggregate`
	* Returns: This function should return a probability in (0,1)
* Optional arguments which are passed to the aggregation function

#### Returns

A DataFrame with columns `question_id`, `probability`, `outcome`,
`answer_option`, where `probability` is the aggregated probability
over the answer option on the question.

One column per `answer_option` on `question_id`.

### `score(forecasts, scoring_rule, *args)`

Score predictions on questions, methods can be given by
the user.

#### Arguments

The type signature of the function is

	score: Dataframe × ([0,1]ⁿ × {0,1}ⁿ × Optional(arguments) -> float) × Optional(arguments) -> DataFrame

To elaborate a bit further:

* First argument (`forecasts`): A DataFrame of the format described [here](#Comparable-Forecast-Data-General-Structure), needs the following columns:
	* `question_id`
	* `probability`
	* `outcome`
	* `answer_option`
* Second argument (`scoring_rule`): The scoring rule for forecasts.
	* Receives:
		* First argument: A numpy array containing the probabilities (in (0,1)
		* Second argument: A numpy array containing the outcomes (in {0,1})
		* Optional arguments passed on by `score`
	* Returns: This function should return a floating point number
* Optional arguments which are passed to the scoring rule

#### Returns

A new DataFrame with the scores for each question: a DataFrame where
the index contains the `question_id`s, and the rows contain the score.

#### Example

We aggregate by calculating the arithmetic mean of all forecasts made
on a question & option, and score with the Brier score:

	def arith_aggr(forecasts):
		return np.array([np.mean(forecasts['probability'])])

	def brier_score(probabilities, outcomes):
		return np.mean((probabilities-outcomes)* *2)

Using these in the repl:

	>>> aggregations=aggregate(survey_forecasts, arith_aggr)
	>>> score(aggregations, brier_score)
	>>> score(aggregations, brier_score)
	question_id
	1001    0.042850
	1002    0.035427
	          ...
	5009    0.049653
	6379    0.046265
	Name: score, Length: 379, dtype: float64

We can now calculate the average Brier score on all questions:

	>>> scores.describe()
	count    379.000000
	mean       0.127762
	std        0.121041
	min        0.005219
	25%        0.035479
	50%        0.071763
	75%        0.189562
	max        0.523622
	Name: score, dtype: float64

### `cumul_user_score(forecasts, scoring_rule, *args)`

Return a new DataFrame that has contains a new field `cumul_score`. The
field contains the past performance of the user making that forecast,
before the time of prediction.

#### Arguments

The type signature of the function is

	cumul_user_score: Dataframe × ([0,1]ⁿ × {0,1}ⁿ × Optional(arguments) -> float) × Optional(arguments) -> DataFrame

* First argument (`forecasts`): a DataFrame with the fields:
	* `question_id`
	* `user_id`
	* `probability`
	* `timestamp`
	* `date_suspend`
* Second argument (`scoring_rule`): the scoring rule by which the performance will be judged
	* Receives:
		* First argument: A numpy array containing the probabilities (in (0,1)
		* Second argument: A numpy array containing the outcomes (in {0,1})
		* Optional arguments passed on by `cumul_user_score`
	* Returns: This function should return a floating point number
* Optional additional arguments that will be passed on to the scoring rule

#### Returns

A new DataFrame that is a copy of `forecasts`, and an additional column
`cumul_score`: The score of the user making the forecast for all
questions that have resolved before the current prediction (that is,
before `timestamp`), as judged by `scoring_rule`.

<!--TODO
#### Example
-->

### `cumul_user_perc(forecasts, lower_better=True)`

Based on cumulative past scores, add the percentile of forecaster
performance the forecaster finds themselves in at the time of forecasting.

#### Arguments

Takes a DataFrame with the columns

* `timestamp`
* `date_suspend`
* `user_id`
* `cumul_score` (e.g. as added by `cumul_user_score`)

and a named argument `lower_better` that, if `True`, assumes that lower
values in `cumul_score` indicate better performance, and if `False`,
assumes that higher values in the same field are better.

#### Returns

The same DataFrame it has received as its argument, and an additional
column `cumul_perc`. `cumul_perc` is the percentile of forecaster
performance the forecaster finds themselves in at the time they are
making the forecast.

#### Notes

The function is currently very slow.

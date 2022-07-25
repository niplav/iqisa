Iqisa Documentation
======================

Iqisa is a library for handling and comparing different forecasting
datasets, focused on taking on the burden of dealing with differently
organised datasets off the user and presenting them with a unified
interface.

On the margin it prioritises correctness over speed, and simplicity over
providing the user with every function they could need.

Examples
--------

### Minimal Example

The minimal steps for getting started with the library are quite
simple. Here's the code for loading the data from the Good Judgment
Project prediction markets:

	$ python3
	>>> import gjp
	>>> import iqisa as iqs
	>>> market_fcasts=gjp.load_markets()

Similarly, one can also load the data from the Good Judgment project
surveys:

	>>> survey_fcasts=gjp.load_surveys()

Now `market_fcasts` contains the forecasts from all prediction markets
from the Good Judgement Project as a [pandas](https://pandas.pydata.org/)
DataFrame<!--TODO: link--> (and `survey_fcasts` all from the surveys):

	>>> market_fcasts
	        question_id  user_id  team_id  probability  ... n_opts          options q_status q_type
	0            1040.0     6203        0       0.4000  ...      2  (a) Yes, (b) No   closed      0
	1            1040.0     6203        0       0.4500  ...      2  (a) Yes, (b) No   closed      0
	...             ...      ...      ...          ...  ...    ...              ...      ...    ...
	793499       1542.0    21975        9       0.0108  ...      2  (a) Yes, (b) No   closed      0
	793500       1542.0    13854       28       0.0049  ...      2  (a) Yes, (b) No   closed      0

	[793501 rows x 15 columns]

The [`load`](#loadfilesNone) functions are the central piece of the
library, as they give you, the user, the data in [a format](#forecasts)
that can be compared across datasets. The other functions are merely
suggestions and can be ignored if they don't fit your use-case (iqisa
wants to provide you with the data, and not be opinionated with what
you do with that data in the end, and how you do it).

### Aggregating and Scoring

The user could now want to just know how good the forecasters were
at forecasting on all questions:

	>>> import numpy as np
	>>> def brier_score(probabilities, outcomes):
	...	return np.mean((probabilities-outcomes)**2)
	>>> scores=iqs.score(market_fcasts, brier_score)
	>>> scores
	                score
	question_id
	1017.0       0.147917
	1038.0       0.177000
	...               ...
	5005.0       0.140392
	6413.0       0.109608

	[411 rows x 1 columns]
	>>> np.mean(scores)
	score    0.137272
	dtype: float64

<!--**-->

Next, the user might define an [aggregation
function](https://forum.effectivealtruism.org/s/hjiBqAJNKhfJFq7kf/p/sMjcjnnpoAQCcedL2):

	>>> import statistics
	>>> import numpy as np
	>>> def geom_odds_aggr(forecasts):
	...    probabilities=forecasts['probability']
	...    probabilities=probabilities/(1-probabilities)
	...    aggregated=statistics.geometric_mean(probabilities)
	...    aggregated=aggregated/(1+aggregated)
	...    return np.array([aggregated])

and use pass it to the `aggregate` method:

	>>> aggregations=iqs.aggregate(market_fcasts, geom_odds_aggr)
	>>> aggregations
	    question_id  probability outcome answer_option
	0        1017.0     0.370863       b             a
	0        1038.0     0.580189       a             a
	..          ...          ...     ...           ...
	0        5005.0     0.194700       a             c
	0        6413.0     0.291428       b             a

	[713 rows x 4 columns]

Now, after aggregating the forecasts, is the Brier score better?

	>>> aggr_scores=iqs.score(aggregations, brier_score)
	>>> aggr_scores
	                score
	question_id
	1017.0       0.137540
	1038.0       0.176242
	...               ...
	5005.0       0.334230
	6413.0       0.058682

	[411 rows x 1 columns]
	>>> np.mean(aggr_scores)
	score    0.083357
	dtype: float64

Yes it is.

### Scoring Users

Unlike for scoring by question, there is no library-internal abstraction
for scoring users, but this is easy to implement:

	def brier_score_user(user_forecasts):
		user_right=(user_forecasts['outcome']==user_forecasts['answer_option'])
		probabilities=user_forecasts['probability']
		return np.mean((probabilities-user_right)**2)

	trader_scores=iqs.score(marrket_fcasts, brier_score, on=['user_id'])

However, we might want to exclude traders who have made fewer than, let's
say, 100 trades:

	filtered_trader_scores=iqs.score(market_fcasts.groupby(['user_id']).filter(lambda x: len(x)>100), brier_score, on=['user_id'])

Surprisingly, the mean score of the traders with >100 trades are not
better than the score of all traders:

	>>> np.mean(trader_scores)
	score    0.159125
	dtype: float64
	>>> np.mean(filtered_trader_scores)
	score    0.159525
	dtype: float64

However, filtering removes outliers (both positive and negative):

	>>> filtered_trader_scores.min()
	score    0.02433
	dtype: float64
	>>> filtered_trader_scores.max()
	score    0.685084
	dtype: float64
	>>> trader_scores.min()
	score    0.0001
	dtype: float64
	>>> trader_scores.max()
	score    0.7921
	dtype: float64

Forecasts & Questions Format
-----------------------------

Iqisa is intended to make forecasting and forecasting question data
from different datasets available in the same data format, which is
described here.

### Forecasts

Some functions (`gjp.load_markets(), gjp.load_surveys(),
metaculus.load_private_binary()`) return data in a common format that
is intended to be comparable across forecasting datasets. That format
is a pandas DataFrame<!--TODO: link--> with shared columns:

<!--TODO: make this a table-->

* `question_id`: The unique ID of the question, type `float64`.
* `user_id`: The unique ID of the user who made the forecast, type `float64`.
* `team_id`: The ID of the team the user was in, type `float64`.
* `probability`: The probability assigned in the forecast, type `float64`. Probabilities (or probabilities implied by market prices) ≥1 are changed to `1-prob_margin` (by default 0.995), and ≤0 to `prob_margin` (by default 0.005).
* `answer_option`: The answer option selected by the user, type `str`.
* `timestamp`: The time at which the forecast/trade was made, type `datetime64[ns]`.
* `outcome`: The outcome of the question, type `str`.
* `open_time`: The time at which the question was opened, i.e. at which forecasts could start. Type `datetime64[ns]`
* `close_time`: The time at which the question was closed, i.e. at which the last possible forecast could be made. Type `datetime64[ns]`.
* `resolve_time`: The time at which the resolution of the question was available. Type `datetime64[ns]`.
* `days_open`: The days for which the quesion was open, type `timedelta64[ns]`.
* `n_opts`: The number of options the question had, type `int64`.
* `options`: A string containing a description of the different possible options, type `str`.
* `q_status`: The status of the question the forecast was made on, type `str`.
* `q_type`: The type of the question, type `int64`.

### Questions

This field is a pandas DataFrame describing the question-specific data in
the dataset. It is set either manually or by calling `load_questions()`
in a subclass.

Its columns are

<!--TODO: describe further-->

* `question_id`, `date_start`, `date_suspend`, `date_to_close`, `date_closed`, `outcome`, `q_type`, `q_status`, `days_open`, `n_opts`, `options`: As in the [description of `forecasts` above](#forecasts)
* `q_title`: The title of the question, as a `str`.

Loading Functions
------------------

The following functions can be used to load the forecasting data.

### `gjp.load_surveys(files=None, processed=True, complete=False)` and `gjp.load_markets(files=None, processed=True, complete=False)`

`gjp.load_surveys()` loads forecasting data from GJP surveys, and
`gjp.load_markets()` loads forecasting data from GJP prediction
markets. They have the same arguments.

#### Arguments

* `files`: If `None`, the data is loaded from the default files (depending on the value of `processed`). Expects a list of strings of the filenames.
	* If `processed` is `True`, `files` is by default `gjp.processed_survey_files`) (for `gjp.load_surveys()`) or `gjp.processed_market_files` (for `gjp.load_markets()`)
	* If `processed` is `False`, `files` is by default `gjp.survey_files` (for `gjp.load_surveys()`) or `gjp.market_files` (for `gjp.load_markets()`)
* `processed`: Whether to load the data from a pre-processed file (if `True`) or from the original files (if `False`). The main difference is in speed, loading from the pre-processed file is much faster.
* `complete`: Whether to load all columns present in the dataset (if `True`) or only columns described [here](#Forecasts) (if `False`). Loading all columns returns a bigger and more confusing DataFrame, loading the comparable subset always returns a subset of the columns of the "complete" DataFrame.

#### Returns

A DataFrame in the format described [here](#Forecasts) loaded from
`files`, potentially with additional columns.

##### Additional Fields when `complete=True`

Setting `complete=True` loads the following additional fields for
`gjp.load_surveys()`:

* `forecast_id`
* `fcast_type`
* `fcast_date`
* `expertise`
* `viewtime`
* `year`
* `q_title`
* `q_desc`
* `short_title`

Setting `complete=True` loads the following additional fields for
`gjp.load_markets()`:

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

#### Data Peculiarities

The GJOpen forecast data has some peculiarities, which are described here:

* `question_id`: Follows the format `[0-9]{4}`.
* `team_id`: The team "DEFAULT" is given the ID 0.
* `answer_option`: One of 'a', 'b', 'c', 'd' or 'e' (or rarely `numpy.nan` for market data).
* `outcome`: One of 'a', 'b', 'c', 'd', or 'e' (or rarely `numpy.nan`, in the case of voided questions).
* `q_status`: One of 'closed', 'voided' or 'open'.
* `q_type`: Integer between 0 and 6 (inclusive).
	* 0: regular binomial or multinomial question
	* 1-5: conditional question, index designated by the specific type (`q_type` 2: 2nd conditional question)
	* 6: Ordered multinomial question

### `gjp.load_questions(files=None)`

Returns a pandas DataFrame with the columns described [here](#Questions)
loaded from `files`, by default from the files listed in
`gjp.questions_files` (value `[./data/gjp/ifps.csv]`).

The field `resolve_time` is the same as `close_time`, as the GJOpen data
doesn't distinguish the two times.

Additionally, this questions data contains the columns

* `q_desc`: The description of the question, including resolution criteria, type `str`.
* `short_title`: The shortened title of the question, type `str`.

### `gjp.survey_files`

A list containing the names of all files in the dataset that contain
data from surveys:

* ./data/gjp/survey_fcasts.yr1.csv
* ./data/gjp/survey_fcasts.yr2.csv
* ./data/gjp/survey_fcasts.yr3.csv.zip
* ./data/gjp/survey_fcasts.yr4.csv.zip

### `gjp.market_files`

A list containing the names of all files in the dataset that contain
trades on prediction markets:

* ./data/gjp/pm_transactions.lum1.yr2.csv
* ./data/gjp/pm_transactions.lum2.yr2.csv
* ./data/gjp/pm_transactions.lum1.yr3.csv
* ./data/gjp/pm_transactions.lum2a.yr3.csv
* ./data/gjp/pm_transactions.lum2.yr3.csv
* ./data/gjp/pm_transactions.inkling.yr3.csv
* ./data/gjp/pm_transactions.control.yr4.csv
* ./data/gjp/pm_transactions.batch.train.yr4.csv
* ./data/gjp/pm_transactions.batch.notrain.yr4.csv
* ./data/gjp/pm_transactions.supers.yr4.csv
* ./data/gjp/pm_transactions.teams.yr4.csv

### `gjp.processed_survey_files` and `gjp.processed_market_files`

Preprocessed files that contain all survey data
(`./data/gjp/surveys.csv.zip`) and all market data
(`./data/gjp/markets.csv.zip`).

### `metaculus.load_private_binary(data_file)`

Load private binary [Metaculus](https://www.metaculus.com/) forecasting
data in the format the Metaculus developers give to researchers.

`data_file` is the path to the file holding the private binary data.

Returns a DataFrame in [this format](#Forecasts). If the Metaculus
questions file in the iqisa repository is outdated this might only load
a subset of the forecasts in `data_file`.

### `metaculus.load_questions(files=None)`

Returns a pandas DataFrame with the columns described [here](#Questions)
loaded from `files`, by default from the files listed in
`metaculus.questions_files` (value `[./data/metaculus/questions.csv]`).

General Functions
------------------

### `aggregate(forecasts, aggregation_function, on=['question_id', 'answer_option'], *args, **kwargs)`

Aggregate forecasts on questions by running `aggregation_function`
over the `forecasts`, aggregation method provided by the user.

#### Arguments

The type signature of the function is

	aggregate: DataFrame × (DataFrame × Optional(arguments) -> [0,1]) × list × Optional(arguments) -> DataFrame

To elaborate a bit further:

* First argument (`forecasts`): A DataFrame of the format described [here](#Forecasts), needs the following columns:
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
* `on`: What columns of `forecasts` to group by/aggregate over. By default the function groups by the question ID and the answer option, so we receive one probability for every answer on every question.
* Optional arguments which are passed to the aggregation function
	* `*args` are the variable arguments, and
	* `**kwargs` are the variable keyword arguments

#### Returns

A DataFrame with columns `probability`, `outcome`, and whatever columns
were specified in the argument `on` (by default `question_id` and
`answer_option`). `probability` is the aggregated probability over the
answer option on the question.

### `score(forecasts, scoring_rule, on=['question_id'] *args, **kwargs)`

Score predictions or aggregated predictions on questions, method can be
given by the user.

#### Arguments

Throws an exception if there are no forecasts loaded/aggregations computed
(i.e. the number of rows of `forecasts`/`aggregations` is zero).

The type signature of the function is

	score: DataFrame × ([0,1]ⁿ × {0,1}ⁿ × Optional(arguments) -> float) × list × Optional(arguments) -> DataFrame

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
* `on`: What columns of `forecasts` to group by/score on. By default the function groups by the question ID , so we receive one score for every question
* Optional arguments which are passed to the scoring rule
	* `*args` are the variable arguments, and
	* `**kwargs` are the variable keyword arguments

#### Returns

A new DataFrame with the scores for each group (as defined by `on`),
by default a DataFrame where the index contains the `question_id`s,
and the rows contain the score.

#### Example

We aggregate by calculating the arithmetic mean of all forecasts made
on a question & option, and score with the Brier score:

	def arith_aggr(forecasts):
		return np.array([np.mean(forecasts['probability'])])

	def brier_score(probabilities, outcomes):
		return np.mean((probabilities-outcomes)**2)

<!--**-->

Using these in the repl:

	>>> import gjp
	>>> import iqisa as iqs
	>>> import numpy as np
	>>> m=gjp.load_markets()
	>>> aggregations=iqs.aggregate(m, arith_aggr)
	>>> aggregations.columns
	Index(['question_id', 'probability', 'outcome', 'answer_option'], dtype='object')
	>>> scores=iqs.score(aggregations, brier_score)
	>>> scores
	question_id
	1017.0       0.140625
	1038.0       0.176400
	...               ...
	5005.0       0.332759
	6413.0       0.081349

	[411 rows x 1 columns]

We can now calculate the average Brier score on all questions:

	>>> scores.describe()
	            score
	count  411.000000
	mean     0.102582
	std      0.100136
	min      0.000574
	25%      0.032574
	50%      0.067686
	75%      0.140791
	max      0.661671

### `add_cumul_user_score(forecasts, scoring_rule, *args, **kwargs)`

Return a new DataFrame that has contains a new field `cumul_score`. The
field contains the past performance of the user making that forecast,
before the time of prediction.

Change `forecasts` so that it has contains a new field `cumul_score`. The
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
before `timestamp`), as judged by `scoring_rule`

### `add_cumul_user_perc(forecasts, lower_better=True)`

Based on cumulative past scores, add the percentile of forecaster
performance the forecaster finds themselves in at the time of forecasting.

#### Arguments

Takes a DataFrame with at least the columns

* `timestamp`
* `date_suspend`
* `user_id`
* `cumul_score` (e.g. as added by `cumul_user_score`)

and a named argument `lower_better` that, if `True`, assumes that lower
values in `cumul_score` indicate better performance, and if `False`,
assumes that higher values in the same field are better.

#### Returns

he same DataFrame it has received as its argument, and an additional
column `cumul_perc`. `cumul_perc` is the percentile of forecaster
performance the forecaster finds themselves in at the time they are
making the forecast.

#### Notes

The function is currently *very* slow (several hours for a dataset of
500k forecasts on my laptop).

### `frontfill(forecasts)`

__Warning__: This function makes the dataset given to it ~100 times
bigger, which might lead to running of out RAM.

Return a new DataFrame with a set of forecasts so that forecasts by
individual forecasters are repeated daily until they make a new forecast
or the question is closed.

#### Arguments

A DataFrame of the format described [here](#Forecasts), necessary columns
are `question_id`, `user_id`, `answer_option`, `timestamp`, `time_close`.

#### Returns

A new DataFrame with a set of forecasts so that forecasts by
individual forecasters are repeated daily until they make a new forecast
or the question is closed.

#### Example

	$ python3
	>>> import gjp
	>>> import iqisa as iqs
	>>> survey_files=['./data/gjp/survey_fcasts_mini.yr1.csv']
	>>> s=gjp.load_surveys(survey_files)
	>>> len(s)
	9999
	>>> s=iqs.frontfill(s)
	>>> len(s)
	940598

### `generic_aggregate(group, summ='arith', format='probs', decay='nodec', extremize='noextr', extrfactor=3, fill=False, expertise=False)`

#### Arguments

#### Returns

#### Example

### `normalise`

Changes the field `aggregations` so that probabilities assigned to
different options on the same question sum to 1.

#### Arguments

None.

#### Returns

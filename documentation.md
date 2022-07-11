Iqisa Documentation
======================

Iqisa is a library for handling and comparing different forecasting
datasets, focused on taking on the burden of dealing with differently
organised datasets off the user and presenting them with a unified
interface.

An Example of Typical Usage
----------------------------

A typical example of someone using the library would begin by the person
importing the library, creating a relevant object and loading the data
from disk:

	>>> import gjp
	>>> m=gjp.Markets()
	>>> m.load()
	>>> m.forecasts.shape
	(510591, 16)

The `load` function might throw some warnings.

The user could now want to just know how good the forecasters were
at forecasting on all questions:

	>>> def brier_score(probabilities, outcomes):
	...	return np.mean((probabilities-outcomes)**2)
	>>> m.score(brier_score)
	>>> m.scores
	                score
	question_id          
	1017.0       0.147917
	1038.0       0.177000
	...               ...
	5005.0       0.140392
	6413.0       0.109608
	>>> np.mean(m.scores)
	score    0.179346

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

	>>> m.aggregate(geom_odds_aggr)
	>>> m.aggregations
	    question_id  probability outcome answer_option
	0        1017.0     0.370863       b             a
	0        1038.0     0.580189       a             a
	..          ...          ...     ...           ...
	0        6413.0     0.215005     NaN             d
	0        6413.0     0.291428     NaN             e
	
	[1127 rows x 4 columns]

Now, after aggregating the forecasts, is the Brier score better?

	>>> m.score_aggregations(brier_score)
	>>> m.scores
	                score
	question_id          
	1017.0       0.137540
	1038.0       0.176242
	...               ...
	5005.0       0.164676
	6413.0       0.060235

	[410 rows x 1 columns]
	>>> >>> np.mean(m.scores)
	score    0.150018
	dtype: float64

Yes it is.

ForecastSetHandler
-------------------

The base class that provides functions for forecast aggregation, scoring
and more.

### `__init__(probmargin=0.005, forecasts=None)`

Constructs the object and initializes `probmargin` and `forecasts`
with the provided value.

### Fields

#### `probmargin`

The value by which probability values of `0` and `1` should be rounded,
type `float`.  Probabilities (or probabilities implied by market prices)
≥1 are changed to `1-probmargin`, and ≤0 to `probmargin`.

#### `with_cumul_scores`

Whether cumulative scores have been added to the forecasts, type
`bool`. `False` by default. Is set to `True` automatically by
`add_cumul_scores`.

#### `time_frontfilled`

Whether frontfilled forecasts have been added to the forecasts,
type `bool`. `False` by default. Is set to `True` automatically by
`frontfill`.

#### `forecasts`

The data returned by any function that loads data from a file with
forecasts or prices from a prediction market, in the format of a pandas
DataFrame. The data for different datasets, or prediction markets and
survey forecasts is slightly different, but they share many columns,
which are described here.

Those columns are:

<!--TODO: make this a table-->

* `question_id`: The unique ID of the question, type `int64`.
* `user_id`: The unique ID of the user who made the forecast, type `int`.
* `team_id`: The ID of the team the user was in, type `int64`.
* `probability`: The probability assigned in the forecast, type `float64`. Probabilities (or probabilities implied by market prices) ≥1 are changed to `1-prob_margin`, and ≤0 to `prob_margin`.
* `answer_option`: The answer option selected by the user, type `str`.
* `timestamp`: The time at which the forecast/trade was made, type `datetime64[ns]`.
* `outcome`: The outcome of the question, type `str`.
* `date_start`: The date at which the question was opened, i.e. at which forecasts could start. Type `datetime64[ns]`
* `date_suspend`: The datetime at which the question was suspended, i.e. at which no further forecasts were possible. Type `datetime64[ns]`. The biggest difference from `date_closed` seems to be that it also includes the time of closures.
* `date_to_close`: The planned closing date of the question, type `datetime64[ns]`.
* `date_closed`: The datetime at which the question was closed, type `datetime64[ns]`.
* `days_open`: The days for which the quesion was open, type `float64`.
* `n_opts`: The number of options the question had, type `int64`.
* `options`: A string containing a description of the different possible options, type `str`.
* `q_status`: The status of the question the forecast was made on, type `str`.
* `q_type`: The type of the question, type `int64`.

This field is set by `load()` or `load_complete()`, or in `__init__`.

#### `questions`

This field is a panas DataFrame describing the question-specific data in
the dataset. It is set either manually or by calling `load_questions()`
in a subclass.

Its columns are

<!--TODO: describe further-->

* `question_id`, `date_start`, `date_suspend`, `date_to_close`, `date_closed`, `outcome`, `q_type`, `q_status`, `days_open`, `n_opts`, `options`: As in the [description of `forecasts` above](#forecasts)
* `q_text`
* `q_desc`
* `short_title`

#### `aggregations`

The data set by `aggregate`, a pandas DataFrame.

Its columns are a subset of the columns of `forecasts`: `question_id`,
`probability`, `outcome` and `answer_option`.

#### `scores`

The data generated by `score` or `score_aggregations`, a pandas
DataFrame. Rows are question IDs (of type `float`, columns are scores
(also type `float`).

### Functions

#### `aggregate(aggregation_function, *args, **kwargs)`

Aggregate forecasts on questions by running `aggregation_functin` over
the field `forecasts`, aggregation method provided by the user.

##### Arguments

Throws an exception if there are no forecasts loaded (i.e. the number
of rows of `forecasts` is zero).

The type signature of the function is

	aggregate: (DataFrame × Optional(arguments) -> [0,1]) × Optional(arguments)

To elaborate a bit further:

* First argument (`aggregation_function`): The user-defined aggregation function, which is called for on each set of forecasts made on the same question for the same answer option.
	* Receives:
		* A DataFrame that is a subset of rows of `forecasts` (all with the same `question_id`)
		* Optional arguments passed on by `aggregate`
	* Returns: This function should return a probability in (0,1)
* Optional arguments which are passed to the aggregation function:
	* `*args` are the variable arguments, and
	* `**kwargs` are the variable keyword arguments

##### Returns

The result of the aggregation is written into the field `aggregations`.

One column per `answer_option` and `question_id` (i.e. one column for
answer option 'a' on question 1, one for answer option 'b' on question 1,
on for answer option 'a' on question 2 etc.).

#### `score(scoring_rule, *args, **kwargs)` and `score_aggregations(scoring_rule, *args, **kwargs)`

Score aggregated predictions on questions, method can be given by
the user.

`score` takes forecasts from the field `forecasts`, while
`score_aggregations` (unsurprisingly) scores forecasts previously
aggregated.

##### Arguments

Throws an exception if there are no forecasts loaded/aggregations computed
(i.e. the number of rows of `forecasts`/`aggregations` is zero).

The type signature of the function is

	score: ([0,1]ⁿ × {0,1}ⁿ × Optional(arguments) -> float) × Optional(arguments)

To elaborate a bit further:

* First argument (`scoring_rule`): The scoring rule for forecasts.
	* Receives:
		* First argument: A numpy array containing the probabilities (in (0,1)
		* Second argument: A numpy array containing the outcomes (in {0,1})
		* Optional arguments passed on by `score`
	* Returns: This function should return a floating point number
* Optional arguments which are passed to the scoring rule:
	* `*args` are the variable arguments, and
	* `**kwargs` are the variable keyword arguments

##### Returns

The results are written onto the field `scores`.

##### Example

We aggregate by calculating the arithmetic mean of all forecasts made
on a question & option, and score with the Brier score:

	def arith_aggr(forecasts):
		return np.array([np.mean(forecasts['probability'])])

	def brier_score(probabilities, outcomes):
		return np.mean((probabilities-outcomes)**2)

<!--**-->

Using these in the repl:

	>>> aggregations=aggregate(arith_aggr)
	>>> m.score(brier_score)
	>>> m.scores
	question_id
	1017.0       0.147917
	1038.0       0.177000
	...               ...
	5005.0       0.140392
	6413.0       0.109608

	[410 rows x 1 columns]

We can now calculate the average Brier score on all questions:

	>>> m.scores.describe()
	            score
	count  410.000000
	mean     0.179346
	std      0.147413
	min      0.006786
	25%      0.069669
	50%      0.141251
	75%      0.248579
	max      0.841011

#### `add_cumul_user_score(scoring_rule, *args, **kwargs)`

Change `forecasts` so that it has contains a new field `cumul_score`. The
field contains the past performance of the user making that forecast,
before the time of prediction.

##### Arguments

`add_cumul_user_score` reads the forecasts from the field `forecasts`,
and writes them back to `forecasts`.

Throws an exception if there are no forecasts loadedcomputed (i.e. the
number of rows of `forecasts` is zero).

The type signature of the function is

	cumul_user_score: ([0,1]ⁿ × {0,1}ⁿ × Optional(arguments) -> float) × Optional(arguments)

* First argument (`scoring_rule`): the scoring rule by which the performance will be judged
	* Receives:
		* First argument: A numpy array containing the probabilities (in (0,1)
		* Second argument: A numpy array containing the outcomes (in {0,1})
		* Optional arguments passed on by `cumul_user_score`
	* Returns: This function should return a floating point number
* Optional additional arguments that will be passed on to the scoring rule

##### Returns

A new DataFrame that is a copy of `forecasts` is written to the field
`forecasts`, with the additional column `cumul_score`: The score of the
user making the forecast for all questions that have resolved before
the current prediction (that is, before `timestamp`), as judged by
`scoring_rule`.

#### `add_cumul_user_perc(lower_better=True)`

Based on cumulative past scores, add the percentile of forecaster
performance the forecaster finds themselves in at the time of forecasting.

##### Arguments

`add_cumul_user_perc` reads from the field `forecasts`, and writes
to it. It throws an exception if the function `add_cumul_user_score`
hasn't been called on the data before.

The function takes one named argument `lower_better` that, if `True`,
assumes that lower values in `cumul_score` indicate better performance,
and if `False`, assumes that higher values in the same field are better.

##### Returns

It writes the result back to the field `forecasts` in the same object.

##### Notes

The function is currently *very* slow (several hours for a dataset of
500k forecasts on my laptop).

#### `frontfill()`

__Warning__: This function makes the dataset given to it ~100 times
bigger, which might lead to running of out RAM.

Return a set of forecasts so that forecasts by individual forecasters are
repeated daily until they make a new forecast or the question is closed.

This function returns a new DataFrame and doesn't change the DataFrame
given as an argument.

##### Arguments

`frontfill` reads from the field `forecasts`, and writes
to it. It throws an exception if the no forecasts have been loaded.

##### Example

	$ python3
	>>> import gjp
	>>> s=gjp.Surveys()
	>>> survey_files=['./data/gjp/survey_fcasts_mini.yr1.csv']
	>>> s.load(survey_files)
	>>> len(s.forecasts)
	9999
	>>> s.frontfill()
	>>> len(s.forecasts)
	1095631

#### `give_frontfilled(forecasts)`

A "static" method that takes a set of forecasts as a DataFrame and
returns the frontfilled DataFrame. Does not change any fields of the
object it belongs to.

##### Arguments

* `forecasts`, a pandas DataFrame, necessary columns are `question_id`, `user_id`, `answer_option`, `timestamp`, `date_closed`

##### Returns

##### Example

#### `generic_aggregate(g, summ='arith', format='probs', decay='nodec', extremize='noextr', extrfactor=3, fill=False, expertise=False)`

##### Arguments

##### Returns

##### Example

#### `normalise`

Changes the field `aggregations` so that probabilities assigned to
different options on the same question sum to 1.

##### Arguments

None.

##### Returns

Nothing, instead mutates the field `aggregations`.

ForecastSetBase
-------------------

Inherits from [ForecastSetHandler](#ForecastSetHandler).

### Fields

#### `questions_files`

The files in which the GJOpen question data is stored, value
'./data/gjp/ifps.csv'.

#### `forecasts`

The GJOpen forecast data has some peculiarities, which are described here:

* `question_id`: Follows the format `[0-9]{4}`.
* `team_id`: The team "DEFAULT" is given the ID 0.
* `answer_option`: One of 'a', 'b', 'c', 'd' or 'e' (or rarely `np.nan` for market data).
* `outcome`: One of 'a', 'b', 'c', 'd', or 'e' (or rarely `np.nan`, in the case of voided questions).
* `q_status`: One of 'closed', 'voided' or 'active'.
* `q_type`: Integer between 0 and 6 (inclusive).
	* 0: regular binomial or multinomial question
	* 1-5: conditional question, index designated by the specific type (`q_type` 2: 2nd conditional question)
	* 6: Ordered multinomial question

### Functions

#### `load_questions(questions_files=None)`

#### `load_complete(files=None)`

#### `load(files=None)`

Markets
-----------

Inherits from [ForecastSetBase](#ForecastSetBase).

### Fields

#### `files`

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

### Functions

#### `load(files=None)`

#### `load_complete(files=None)`

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

Surveys
-----------

Inherits from [ForecastSetBase](#ForecastSetBase).

### Fields

#### `files`

A list containing the names of all files in the dataset that contain
data from surveys:

* ./data/gjp/survey_fcasts.yr1.csv
* ./data/gjp/survey_fcasts.yr2.csv
* ./data/gjp/survey_fcasts.yr3.csv.zip
* ./data/gjp/survey_fcasts.yr4.csv.zip

### Functions

#### `load(files=None)`

#### `load_complete(files=None)`

* `forecast_id`
* `fcast_type`
* `fcast_date`
* `expertise`
* `viewtime`
* `year`
* `q_text`
* `q_desc`
* `short_title`

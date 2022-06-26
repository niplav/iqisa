Data Structures
----------------

### Forecast Data General Structure

The data returned by any function that loads data from a file with
forecasts or prices from a prediction market, in the format of a pandas
DataFrame. The data for prediction markets and survey forecasts is
slightly different, but they share many fields, which are described here.

Those fields are:

* `question_id`: The unique ID of the question, type `str`. Follows the format `[0-9]{4}`.
* `user_id`: The unique ID of the user who made the forecast, type `int`.
* `team_id`: The ID of the team the user was in, type `int64`. The team "DEFAULT" was given the ID 0.
* `probability`: The probability assigned in the forecast, type `float64`. Probabilities (or probabilities implied by market prices) ≥1 were changed to 0.995, and ≤0 to 0.005.
* `answer_option`: The answer option selected by the user, type `str`. One of 'a', 'b', 'c', 'd' or 'e' (or rarely `np.nan` for market data).
* `timestamp`: The time at which the forecast/trade was made, type `datetime64[ns]`.
* `outcome`:
* `date_start`:
* `date_suspend`:
* `date_to_close`:
* `date_closed`:
* `days_open`:
* `n_opts`:
* `options`:
* `q_status`:
* `q_type`:
* `cond`: The index of the question as a conditional question. Some questions are conditional, these conditional questions can be grouped together. (Example (not in the dataset): "If the air pollution in Beijing is {higher, lower} than 15 PM 2.5 on average in 2012 [this is the conditional], will the average life expectancy be higher than in 2010? [this is the question]"). These two questions would have values `1` and `2` on the `cond` column.
	* Apparently questions which are not conditional receive a value of 1 on the `cond` column, even though their `question_id` has the postfix `-0`.
* `team`: The ID of the team the user was in. Number between 1 and 50.
* `training`: The amount of training the user received. String in the format `[a-d]`, described further in `user_type`. I don't know what `d` refers to here.
* `user_type`: The type of user, as a string. Follows an idiosyncratic format, the full description from the README of the original data explains it (the prediction market types with prefix '3' are not used in this dataset):
	* Individuals
		* 1a   = Individual w/o training (all years)
		* 1b   = Individual w/ probability training (all years)
		* 1c   = Individual w/ scenario training (year 1)
		* 1h   = Individual w/ training; Hybrid-Accountability (year 4)
		* 1n   = MOOF platform with NCBP scoring (year 4)
		* 1p   = Individual w/ training; Process-Accountability (year 4)
		* 1r1  = MOOF raters (individuals) (year 4)
		* 1u   = MOOF platform untrained individuals [no train](year 4)
		* 1z   = MOOF platform standard participant (year 4)
	* Individuals who could see crowd information
		* 2a   = Crowd information w/o training (year 1)
		* 2b   = Crowd information w/ probability training (year 1)
		* 2c   = Crowd information w/ scenario training (year 1)
	* Teams (xx = team\_id)
		* 4axx = Teams without training (year 1 & 2)
		* 4bxx = Teams with training(all years); Outcome Accountability (year 4)
		* 4cxx = Teams with scenario training (year 1)
		* 4dxx = Teams with training and facilitators (year 3)
		* 4hx  = Teams with training; Hybrid Accountability (year 4)
		* 4px  = Teams with training; Process Accountability (year 4)
		* 4uxx = Team size experiment with smaller teams (year 4)
		* 4wxx = Team size experiment with larger teams (year 4)
	* Superforecasters (xx = team\_id)
		* 5bxx = Superteams with training (year 2)
		* 5dxx = Superteams with training and facilitators (year 3)
		* 5sxx = Superteams with training; Outcome Accountability (year 4)
* `forecast_id`
* `fcast_type`
* `answer_option`
* `probability`
* `fcast_date`
* `expertise`
* `q_status`
* `viewtime`
* `year`
* `timestamp`
* `q_type`
* `date_start`
* `date_suspend`
* `date_to_close`
* `date_closed`
* `outcome`
* `days_open`
* `n_opts`

Functions
----------

### `frontfill_forecasts`

__Warning__: This function makes the dataset given to it ~100 times
bigger, which might lead to running of out RAM.

Modify a set of forecasts so that forecasts by individual forecasters are
repeated daily until they make a new forecast or the question is closed.

#### Arguments

A DataFrame of the format described [here](#Returns_2).

Specifically, the DataFrame should have the following columns:

* `question_id`
* `user_id`
* `answer_option`
* `fcast_date`
* `timestamp`

#### Returns

A DataFrame of the formate described [here](#Returns_2).

#### Example

	$ python3 -i gjplib.py
	>>> survey_files=['./data/survey_fcasts_mini.yr1.csv']
	>>> survey_forecasts=get_survey_forecasts()
	>>> len(survey_forecasts)
	9999
	>>> survey_forecasts=frontfill_forecasts(survey_forecasts)
	>>> len(survey_forecasts)
	1095705

### `calculate_aggregate_score`

Aggregate and score predictions on questions, methods can be given by
the user.

#### Arguments

* First argument (`forecasts`): A DataFrame of the format described [here](#Returns_2), needs the following columns:
	* `question_id`
	* `timestamp`
	* `probability`
	* `answer_option`
	* `outcome`
* Second argument (`aggregation_function`): The user-defined aggregation function, which is called for on each set of forecasts made on the same question for the same answer option.
	* Receives: A DataFrame that is a subset of columns of `forecasts`
	* Returns: This function should return a single probability in (0,1)
* Third argument (`scoring_rule`): The scoring rule for forecasts.
	* Receives:
		* First argument: A numpy array containing the probabilities (in (0,1)
		* Second argument: A numpy array containing the outcomes (in {0,1})
	* Returns: This function should return a floating point number

#### Returns

The scores for each question: a DataFrame where the index contains the
`question_id`s, and the columns contain the score.

#### Example

We aggregate by calculating the arithmetic mean of all forecasts made
on a question & option, and score with the Brier score:

	def arith_aggr(forecasts):
	        return np.array([np.mean(forecasts['probability'])])

	def brier_score(probabilities, outcomes):
	        return np.mean((probabilities-outcomes)**2)

Using these in the repl:

	>>> scores=calculate_aggregate_score(survey_forecasts, arith_aggr, brier_score)
	>>> print(scores)
	                score
	question_id
	1001-0       0.042850
	1002-0       0.035197
	...               ...
	5009-0       0.049653
	6379-0       0.046265
	[462 rows x 1 columns]

We can now calculate the average Brier score on all questions:

	>>> scores.describe()
	            score
	count  462.000000
	mean     0.130377
	std      0.122574
	min      0.002113
	25%      0.033316
	50%      0.071521
	75%      0.250116
	max      0.523622

### `get_survey_forecasts`

Reads & returns a datastructure containing all forecasts reported by
forecasters in surveys (that is, all forecasts not made on a prediction
market).

#### Arguments

None.

#### Returns

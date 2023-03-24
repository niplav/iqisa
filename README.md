Iqisa: A Library For Handling Forecasting Datasets
===================================================

Iqisa is a collection of forecasting datasets and a simple
library for handling those datasets. Code and data available
[here](https://github.com/niplav/iqisa).

So far it contains data from the [Good Judgment
Project](https://en.wikipedia.org/wiki/The_Good_Judgment_Project) and
code for handling the private [Metaculus](https://metaculus.com) data
(available on request to Metaculus for researchers), but I plan to also
add data from various other sources.

The documentation can be found [here](./iqisadoc.html), but a simple
example for using the library is seeing whether traders with more than
100 trades have a better Brier score than traders in general:

	import gjp
	import iqisa as iqs
	market_fcasts=gjp.load_markets()

	def brier_score(probabilities, outcomes):
		return np.mean((probabilities-outcomes)**2)

	def brier_score_user(user_forecasts):
		user_right=(user_forecasts['outcome']==user_forecasts['answer_option'])
		probabilities=user_forecasts['probability']
		return np.mean((probabilities-user_right)**2)

	trader_scores=iqs.score(market_fcasts, brier_score, on=['user_id'])
	filtered_trader_scores=iqs.score(market_fcasts.groupby(['user_id']).filter(lambda x: len(x)>100), brier_score, on=['user_id'])

And we can see:

	>>> np.mean(trader_scores)
	score    0.159194
	dtype: float64
	>>> np.mean(filtered_trader_scores)
	score    0.159018
	dtype: float64

Concluding that more experienced traders are only very slightly better
at trading.

Usages
-------

* [Range and Forecasting Accuracy (niplav, 2023)](https://niplav.github.io/range_and_forecasting_accuracy#Analysis__Results)

Potential Additional Sources for Forecasting Data
--------------------------------------------------

* [Metaforecast API](https://metaforecast.org/api/graphql?query=%23%0A%23+Welcome+to+Yoga+GraphiQL%0A%23%0A%23+Yoga+GraphiQL+is+an+in-browser+tool+for+writing%2C+validating%2C+and%0A%23+testing+GraphQL+queries.%0A%23%0A%23+Type+queries+into+this+side+of+the+screen%2C+and+you+will+see+intelligent%0A%23+typeaheads+aware+of+the+current+GraphQL+type+schema+and+live+syntax+and%0A%23+validation+errors+highlighted+within+the+text.%0A%23%0A%23+GraphQL+queries+typically+start+with+a+%22%7B%22+character.+Lines+that+start%0A%23+with+a+%23+are+ignored.%0A%23%0A%23+An+example+GraphQL+query+might+look+like%3A%0A%23%0A%23+++++%7B%0A%23+++++++field%28arg%3A+%22value%22%29+%7B%0A%23+++++++++subField%0A%23+++++++%7D%0A%23+++++%7D%0A%23%0A%23+Keyboard+shortcuts%3A%0A%23%0A%23++Prettify+Query%3A++Shift-Ctrl-P+%28or+press+the+prettify+button+above%29%0A%23%0A%23+++++Merge+Query%3A++Shift-Ctrl-M+%28or+press+the+merge+button+above%29%0A%23%0A%23+++++++Run+Query%3A++Ctrl-Enter+%28or+press+the+play+button+above%29%0A%23%0A%23+++Auto+Complete%3A++Ctrl-Space+%28or+just+start+typing%29%0A%23%0A)
* [PredictionBook](http://predictionbook.com/)
* [Foretell (CSET)](https://www.cset-foretell.com/)
* [Good Judgment Open](https://www.gjopen.com/)
* [Hypermind](https://www.hypermind.com)
* [Augur](https://augur.net/)
* [Foretold](https://www.foretold.io/)
* [Omen](https://www.fsu.gr/en/fss/omen)
* [GiveWell](https://www.givewell.org/)
* [Open Philanthropy Project](https://www.openphilanthropy.org/)
* [PredictIt](https://www.predictit.org/)
* [Elicit](https://elicit.org/)
* [PolyMarket](https://polymarket.com/)
* [Iowa Electronic Markets](https://en.wikipedia.org/wiki/Iowa_Electronic_Markets)
* [INFER](https://www.infer-pub.com/)
* [Manifold](https://manifold.markets/home)
* [Smarkets](https://smarkets.com/)
* [The Odds API](https://the-odds-api.com/)

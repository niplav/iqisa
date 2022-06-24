import re
import time
import random
import math
import datetime as dt
import numpy as np
import pandas as pd

PROB_MARGIN=0.005

survey_files=["./data/gjp/survey_fcasts.yr1.csv", "./data/gjp/survey_fcasts.yr2.csv", "./data/gjp/survey_fcasts.yr3.csv"]
questions_files=["./data/gjp/ifps.csv"]

year2_default_changes={
	'fixes': ['timestamp', 'question_id_no_zero', 'price_before_100', 'question_id_str'],
	'column_rename': {
		'IFPID': 'question_id',
		'user.ID': 'user_id',
		'Op.Type': 'op_type',
		'order.ID': 'order_id',
		'buy': 'isbuy',
		'long': 'islong',
		'with.MM': 'with_mm',
		'matching.order.ID': 'matching_order_id',
		'price': 'price_before_prob',
		'qty': 'quantity',
		'by.agent': 'by_agent',
	}
}

year3_default_changes={
	'fixes': ['timestamp', 'price_before_100', 'price_after_100', 'prob_est_100', 'question_id_str'],
	'column_rename': {
		'IFPID': 'question_id',
		'Outcome': 'outcome',
		'User.ID': 'user_id',
		'Op.Type': 'op_type',
		'Order.ID': 'order_id',
		'isBuy': 'isbuy',
		'isLong': 'islong',
		'With.MM': 'with_mm',
		'By.Agent': 'by_agent',
		'Matching.Order.ID': 'matching_order_id',
		'Order.Price': 'price_before_prob',
		'Order.Qty': 'quantity',
		'Trade.Price': 'price_after_prob',
		'Trade.Qty': 'trade_qty',
		'Tru.Belief': 'prob_est',
		'Low.Fuse': 'low_fuse',
		'Max.Bid': 'max_bid',
		'Min.Ask': 'min_ask',
		'High.Fuse': 'high_fuse',
		'Min.Qty': 'min_qty',
		'Divest.Only': 'divest_only',
	}
}

year4_default_changes={
	'fixes': ['created_date_us', 'filled_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'question_id_str', 'id_in_name', 'insert_outcomes', 'option_from_stock_name'],
	'column_rename': {
		'Trade.ID': 'trade_id',
		'Market.Name': 'market_name',
		'Stock.Name': 'stock_name',
		'Trade.Type': 'trade_type',
		'Quantity': 'quantity',
		'Spent': 'spent',
		'Created.At': 'created_at',
		'Filled.At': 'filled_at',
		'Price.Before': 'price_before_prob',
		'Price.After': 'price_after_prob',
		'Probability.Estimate': 'prob_est',
		'GJP.User.ID': 'user_id'
	}
}

market_files={
	'./data/gjp/pm_transactions.lum1.yr2.csv': year2_default_changes,
	'./data/gjp/pm_transactions.lum2.yr2.csv': 	year2_default_changes,
	'./data/gjp/pm_transactions.lum1.yr3.csv': year3_default_changes,
	'./data/gjp/pm_transactions.lum2a.yr3.csv': year3_default_changes,
	'./data/gjp/pm_transactions.lum2.yr3.csv': {
		'fixes': ['timestamp', 'question_id_no_zero', 'price_before_100', 'prob_est_100', 'question_id_str'],
		'column_rename': {
			'IFPID': 'question_id',
			'Outcome': 'outcome',
			'User.ID': 'user_id',
			'Team': 'team_id',
			'Op.Type': 'op_type',
			'Order.ID': 'order_id',
			'isBuy': 'isbuy',
			'isLong': 'islong',
			'With.MM': 'with_mm',
			'By.Agent': 'by_agent',
			'Matching.Order.ID': 'matching_order_id',
			'Order.Price': 'price_before_prob',
			'Order.Qty': 'quantity',
			'Trade.Price': 'price_after_prob',
			'Trade.Qty': 'trade_qty',
			'Tru.Belief': 'prob_est',
			'Low.Fuse': 'low_fuse',
			'Max.Bid': 'max_bid',
			'Min.Ask': 'min_ask',
			'High.Fuse': 'high_fuse',
			'Min.Qty': 'min_qty',
			'Divest.Only': 'divest_only',
		}
	},
	'./data/gjp/pm_transactions.inkling.yr3.csv': {
		'fixes': ['created_date_us', 'filled_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'id_by_name', 'option_from_stock_name'],
		'column_rename': {
			'trade.id': 'trade_id',
			'market.name': 'market_name',
			'stock.name': 'stock_name',
			'type': 'op_type',
			'created.at': 'created_at',
			'filled.at': 'filled_at',
			'price_before': 'price_before_prob',
			'price_after': 'price_after_prob',
			'probability_estimate': 'prob_est',
			'gjp.user.id': 'user_id'
		}
	},
	'./data/gjp/pm_transactions.teams.yr4.csv': {
		'fixes': ['created_date_us', 'filled_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'question_id_str', 'id_in_name', 'insert_outcome', 'option_from_stock_name'],
		'column_rename': {
			'Trade.ID': 'trade_id',
			'Market.Name': 'market_name',
			'Stock.Name': 'stock_name',
			'Trade.Type': 'trade_type',
			'Quantity': 'quantity',
			'Spent': 'spent',
			'Created.At': 'created_at',
			'Filled.At': 'filled_at',
			'Price.Before': 'price_before_prob',
			'Price.After': 'price_after_prob',
			'Probability.Estimate': 'prob_est',
			'GJP.Team.ID': 'team_id',
			'GJP.User.ID': 'user_id'
		}
	},
	'./data/gjp/pm_transactions.batch.notrain.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.control.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.batch.notrain.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.supers.yr4.csv': year4_default_changes,
}

def extract_id(s):
	p=re.compile('^[0-9]+')
	return str(p.findall(s)[0])

def simplify_id(s):
	p=re.compile('^[0-9]+')
	return p.findall(s)[0] if type(s)==str else s

# the data has trades on markets, stock names (sn) are possibly substrings
# of the options, preceded by the name of the option [a-e].
# yeah, i don't know either why anyone would do this.

def get_option_from_options(t):
	n=t[1]
	sn=t[0]
	#for some reason (!?) the answer options may contain these
	sne=re.escape(sn.replace('**', ''))
	n=n.replace('**', '')
	p=re.compile('\((.)\) ?'+sne)
	finds=p.findall(n)
	if len(finds)==1:
		return finds[0]
	# the conditional came to pass
	p=re.compile(sne+'[^\(]+\((.)\)')
	finds=p.findall(n)
	if len(finds)==1:
		return finds[0]
	# the conditional didn't come to pass
	p=re.compile('\((.)\)[^\(]+$')
	finds=p.findall(n)
	if len(finds)==1:
		return finds[0]
	return '' # give up, but this dsnesn't happen on the current data

def get_market_forecasts():
	market_forecasts=pd.DataFrame()

	questions=get_questions()
	questions.loc[:,'question_id']=questions['question_id'].map(simplify_id)

	for f in market_files.keys():
		market=pd.read_csv(f)
		market=market.rename(columns=market_files[f]['column_rename'], errors='raise')

		if 'id_in_name' in market_files[f]['fixes']:
			market['question_id']=market['market_name'].map(extract_id)
		if 'created_date_us' in market_files[f]['fixes']:
			market['created_at']=pd.to_datetime(market['created_at'], dayfirst=True)
		if 'filled_date_us' in market_files[f]['fixes']:
			market['filled_at']=pd.to_datetime(market['filled_at'], dayfirst=True)
		if 'timestamp' in market_files[f]['fixes']:
			market['timestamp']=pd.to_datetime(market['timestamp'], dayfirst=True)
		if 'price_before_perc' in market_files[f]['fixes']:
			market['price_before_prob']=market['price_before_prob'].map(lambda x: float(x.replace('%', ''))/100)
		if 'price_after_perc' in market_files[f]['fixes']:
			market['price_after_prob']=market['price_after_prob'].map(lambda x: float(x.replace('%', ''))/100)
		if 'prob_est_perc' in market_files[f]['fixes']:
			strperc=market.loc[market['prob_est'].map(type)==str]
			market.loc[market['prob_est'].map(type)==str, 'prob_est']=strperc['prob_est'].map(lambda x: np.nan if x=='no' else float(x.replace('%', ''))/100)
		if 'price_before_100' in market_files[f]['fixes']:
			market['price_before_prob']=market['price_before_prob'].map(lambda x: float(x))/100
		if 'price_after_100' in market_files[f]['fixes']:
			market['price_after_prob']=market['price_after_prob'].map(lambda x: float(x))/100
		if 'prob_est_100' in market_files[f]['fixes']:
			market['prob_est']=market['prob_est'].map(lambda x: float(x))/100
		if 'question_id_str' in market_files[f]['fixes']:
			market['question_id']=market['question_id'].map(str)
		if 'insert_outcome' in market_files[f]['fixes']:
			q_outcomes=questions.loc[questions['question_id'].isin(market['question_id'])][['question_id', 'outcome']]
			market=pd.merge(market, q_outcomes, on='question_id', how='inner')

			# TODO: this leaves the data with too many rows!
			# Somehow the join here is still "too big" :-$

		if 'id_by_name' in market_files[f]['fixes']:
			q_texts=questions.loc[questions['q_text'].isin(market['market_name'])][['question_id','q_text']]
			market=pd.merge(market, q_texts, left_on='market_name', right_on='q_text', how='inner')

			market.pop('q_text')

		if 'option_from_stock_name' in market_files[f]['fixes']:
			q_options=questions[['question_id','options']]
			with_options=pd.merge(market, q_options, on='question_id', how='inner')
			market['answer_option']=with_options[['stock_name', 'options']].apply(get_option_from_options, axis=1)

		market_forecasts=pd.concat([market_forecasts, market], join='outer')

	# add the some question-specific information to the trades
	# TODO: I'm not actually sure this is correct!
	qdata=questions.loc[questions['question_id'].isin(market_forecasts['question_id'])][['question_id', 'date_closed', 'date_start', 'date_suspend', 'date_to_close', 'days_open', 'n_opts', 'options', 'q_status', 'q_type']]
	market_forecasts=pd.merge(market_forecasts, qdata, on='question_id', how='inner')
	# prices in (-∞,0]∪[1,∞] are truncated to [MIN_PROB, 1-MIN_PROB]

	market_forecasts.loc[market_forecasts['price_before_prob']<=0, 'price_before_prob']=PROB_MARGIN
	market_forecasts.loc[market_forecasts['price_before_prob']>=1, 'price_before_prob']=1-PROB_MARGIN

	market_forecasts.loc[market_forecasts['price_after_prob']<=0, 'price_after_prob']=PROB_MARGIN
	market_forecasts.loc[market_forecasts['price_after_prob']>=1, 'price_after_prob']=1-PROB_MARGIN

	market_forecasts.loc[market_forecasts['prob_est']<=0, 'prob_est']=PROB_MARGIN
	market_forecasts.loc[market_forecasts['prob_est']>=1, 'prob_est']=1-PROB_MARGIN

	return market_forecasts

def get_questions():
	questions=pd.DataFrame()

	for f in questions_files:
		questions=pd.concat([questions, pd.read_csv(f)])

	date_fields=['date_start', 'date_suspend', 'date_to_close', 'date_closed']

	for f in date_fields:
		questions[f]=pd.to_datetime(questions[f], dayfirst=True)

	questions=questions.rename(columns={'ifp_id': 'question_id'}, errors="raise")

	return questions

def get_survey_forecasts():
	survey_forecasts=pd.DataFrame()

	for f in survey_files:
		survey_forecasts=pd.concat([survey_forecasts, pd.read_csv(f)])

	survey_forecasts['timestamp']=pd.to_datetime(survey_forecasts['timestamp'])
	survey_forecasts['fcast_date']=pd.to_datetime(survey_forecasts['fcast_date'])

	survey_forecasts=survey_forecasts.rename(columns={'ifp_id': 'question_id', 'value': 'probability'}, errors="raise")

	questions=get_questions()

	survey_forecasts=pd.merge(survey_forecasts, questions, on='question_id', suffixes=(None, '_x'))

	unnecessary_columns=['q_text', 'q_desc', 'short_title', 'options', 'q_status_x']

	for c in unnecessary_columns:
		survey_forecasts.pop(c)

	survey_forecasts=survey_forecasts.rename(columns={'ctt': 'user_type'}, errors="raise")

	survey_forecasts.loc[survey_forecasts['probability']==0, 'probability']=PROB_MARGIN
	survey_forecasts.loc[survey_forecasts['probability']==1, 'probability']=1-PROB_MARGIN

	return survey_forecasts

def frontfill_forecasts(forecasts):
	"""forecasts should be a dataframe with at least these five fields:
	question_id, user_id, timestamp, probability"""
	res=survey_forecasts.groupby(['question_id', 'user_id', 'answer_option']).apply(frontfill_group)
	res.index=res.index.droplevel(['question_id', 'user_id', 'answer_option'])
	return res

def frontfill_group(g):
	"""warning: this makes the forecast ids useless"""
	dates=pd.date_range(start=min(g.timestamp), end=max(g.date_closed), freq='D')
	alldates=pd.DataFrame({'fcast_date': dates})
	g=g.merge(alldates, on='fcast_date', how='outer')
	g=g.sort_values(by='fcast_date')
	g['timestamp']=g['timestamp'].fillna(g['fcast_date'])
	g=g.fillna(method='ffill')
	return g

def calculate_aggregate_score(forecasts, aggregation_function, scoring_rule):
	"""forecasts should be a pandas.DataFrame that contains columns
	question_id, user_id, timestamp, probability, answer_option, outcome, date_closed"""
	res=survey_forecasts.groupby(['question_id', 'answer_option']).apply(apply_aggregation, aggregation_function)
	res.index=res.index.droplevel(['question_id', 'answer_option'])
	res=res.groupby(['question_id']).apply(apply_score, scoring_rule)
	res.index=res.index.droplevel(1)
	return res

def apply_aggregation(g, aggregation_function):
	transformed_probs=aggregation_function(g)
	return pd.DataFrame({'question_id': np.array(g['question_id'])[0], 'probability': transformed_probs, 'outcome': np.array(g['outcome'])[0], 'answer_option': np.array(g['answer_option'])[0]})

def apply_score(g, scoring_rule):
	probabilities=np.array(g['probability'])
	outcomes=np.array(g['outcome'])
	options=np.array(g['answer_option'])
	return pd.DataFrame({'score': np.array([scoring_rule(probabilities, outcomes==options)])})

def arith_aggr(forecasts):
	return np.array([np.mean(forecasts['probability'])])

def brier_score(probabilities, outcomes):
	return np.mean((probabilities-outcomes)**2)

def usuniq(l):
	c=dict()
	for e in l:
		c[e]=True
	return c.keys()

survey_forecasts=get_survey_forecasts()
questions=get_questions()
#survey_forecasts=frontfill_forecasts(survey_forecasts)
market_forecasts=get_market_forecasts()

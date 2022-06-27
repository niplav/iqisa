import re
import time
import random
import math
import statistics
import datetime as dt
import numpy as np
import pandas as pd

PROB_MARGIN=0.005

comparable_index=['question_id', 'user_id', 'team_id', 'probability', 'answer_option', 'timestamp', 'outcome', 'date_start', 'date_suspend', 'date_to_close', 'date_closed', 'days_open', 'n_opts', 'options', 'q_status', 'q_type']

survey_files=['./data/gjp/survey_fcasts.yr1.csv', './data/gjp/survey_fcasts.yr2.csv', './data/gjp/survey_fcasts.yr3.csv']
market_files=['./data/gjp/pm_transactions.lum1.yr2.csv', './data/gjp/pm_transactions.lum2.yr2.csv', './data/gjp/pm_transactions.lum1.yr3.csv', './data/gjp/pm_transactions.lum2a.yr3.csv', './data/gjp/pm_transactions.lum2.yr3.csv', './data/gjp/pm_transactions.inkling.yr3.csv', './data/gjp/pm_transactions.control.yr4.csv', './data/gjp/pm_transactions.batch.train.yr4.csv', './data/gjp/pm_transactions.batch.notrain.yr4.csv', './data/gjp/pm_transactions.supers.yr4.csv', './data/gjp/pm_transactions.teams.yr4.csv']
questions_files=['./data/gjp/ifps.csv']

year2_default_changes={
	'fixes': ['timestamp', 'price_before_100', 'question_id_str', 'insert_outcomes', 'without_team_id'],
	'column_rename': {
		'IFPID': 'question_id',
		# yes. I check, for example with question 1214-0, the outcome is b, but most of the trades are on 'a'.
		'outcome': 'answer_option',
		'user.ID': 'user_id',
		'Op.Type': 'op_type',
		'order.ID': 'order_id',
		'buy': 'isbuy',
		'long': 'islong',
		'with.MM': 'with_mm',
		'matching.order.ID': 'matching_order_id',
		'price': 'probability',
		'qty': 'quantity',
		'by.agent': 'by_agent',
	}
}

year3_default_changes={
	'fixes': ['timestamp', 'price_before_100', 'price_after_100', 'prob_est_100', 'question_id_str', 'insert_outcomes', 'with_prob_est', 'without_team_id'],
	'column_rename': {
		'IFPID': 'question_id',
		# same as above
		'Outcome': 'answer_option',
		'User.ID': 'user_id',
		'Op.Type': 'op_type',
		'Order.ID': 'order_id',
		'isBuy': 'isbuy',
		'isLong': 'islong',
		'With.MM': 'with_mm',
		'By.Agent': 'by_agent',
		'Matching.Order.ID': 'matching_order_id',
		'Order.Price': 'probability',
		'Order.Qty': 'quantity',
		'Trade.Price': 'prob_after_trade',
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
	'fixes': ['timestamp', 'created_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'question_id_str', 'id_in_name', 'insert_outcomes', 'option_from_stock_name', 'with_prob_est', 'without_team_id'],
	'column_rename': {
		'Trade.ID': 'order_id',
		'Market.Name': 'market_name',
		'Stock.Name': 'stock_name',
		'Trade.Type': 'trade_type',
		'Quantity': 'quantity',
		'Spent': 'spent',
		'Created.At': 'created_at',
		'Filled.At': 'timestamp',
		'Price.Before': 'probability',
		'Price.After': 'prob_after_trade',
		'Probability.Estimate': 'prob_est',
		'GJP.User.ID': 'user_id'
	}
}

market_files_fixes={
	'./data/gjp/pm_transactions.lum1.yr2.csv': year2_default_changes,
	'./data/gjp/pm_transactions.lum2.yr2.csv': year2_default_changes,
	'./data/gjp/pm_transactions.lum1.yr3.csv': year3_default_changes,
	'./data/gjp/pm_transactions.lum2a.yr3.csv': year3_default_changes,
	'./data/gjp/pm_transactions.lum2.yr3.csv': {
		'fixes': ['timestamp', 'price_before_100', 'prob_est_100', 'question_id_str', 'team_bad', 'with_after_trade', 'with_prob_est'],
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
			'Order.Price': 'probability',
			'Order.Qty': 'quantity',
			'Trade.Price': 'prob_after_trade',
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
		'fixes': ['timestamp', 'created_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'id_by_name', 'option_from_stock_name', 'with_after_trade', 'with_prob_est', 'without_team_id'],
		'column_rename': {
			'trade.id': 'order_id',
			'market.name': 'market_name',
			'stock.name': 'stock_name',
			'type': 'op_type',
			'created.at': 'created_at',
			'filled.at': 'timestamp',
			'price_before': 'probability',
			'price_after': 'prob_after_trade',
			'probability_estimate': 'prob_est',
			'gjp.user.id': 'user_id'
		}
	},
	'./data/gjp/pm_transactions.teams.yr4.csv': {
		'fixes': ['timestamp', 'created_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'question_id_str', 'id_in_name', 'insert_outcome', 'option_from_stock_name', 'with_after_trade', 'with_prob_est'],
		'column_rename': {
			'Trade.ID': 'order_id',
			'Market.Name': 'market_name',
			'Stock.Name': 'stock_name',
			'Trade.Type': 'trade_type',
			'Quantity': 'quantity',
			'Spent': 'spent',
			'Created.At': 'created_at',
			'Filled.At': 'timestamp',
			'Price.Before': 'probability',
			'Price.After': 'prob_after_trade',
			'Probability.Estimate': 'prob_est',
			'GJP.Team.ID': 'team_id',
			'GJP.User.ID': 'user_id'
		}
	},
	'./data/gjp/pm_transactions.batch.train.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.batch.notrain.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.control.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.batch.notrain.yr4.csv': year4_default_changes,
	'./data/gjp/pm_transactions.supers.yr4.csv': year4_default_changes,
}

def extract_id(s):
	p=re.compile('^[0-9]+')
	return str(p.findall(s)[0])

def extract_type(s):
	p=re.compile('-([0-6])$')
	return int(p.findall(s)[0])

def simplify_id(s):
	p=re.compile('^[0-9]+')
	return p.findall(s)[0] if type(s)==str else s

def extract_team(s):
	if s=='DEFAULT':
		return 0 # team ID 0 has not been given.
	p=re.compile('e([0-9]{1,2})$')
	return int(p.findall(s)[0])

# the data has trades on markets, stock names (sn) are possibly substrings
# of the options, preceded by the name of the option [a-e].
# yeah, i don't know why anyone would do this either.

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

def get_market_forecasts(files):
	market_forecasts=pd.DataFrame()

	questions=get_questions()
	questions=questions.loc[questions['q_status']!='voided']

	for f in files:
		market=pd.read_csv(f)
		market=market.rename(columns=market_files_fixes[f]['column_rename'], errors='raise')
		print(len(market))

		#We want to use question_id below, but we want it to
		#have the correct type already, so sometimes we have to
		#generate it from other data.
		if 'id_by_name' in market_files_fixes[f]['fixes']:
			q_texts=questions[['question_id','q_text']]
			market=pd.merge(market, q_texts, left_on='market_name', right_on='q_text', how='inner')
			market.pop('q_text')
		if 'id_in_name' in market_files_fixes[f]['fixes']:
			market['question_id']=market['market_name'].map(extract_id)

		market['question_id']=pd.to_numeric(market['question_id'])

		if 'created_date_us' in market_files_fixes[f]['fixes']:
			market['created_at']=pd.to_datetime(market['created_at'], dayfirst=True)
		if 'timestamp' in market_files_fixes[f]['fixes']:
			market['timestamp']=pd.to_datetime(market['timestamp'], dayfirst=True)
		if 'price_before_perc' in market_files_fixes[f]['fixes']:
			market['probability']=market['probability'].map(lambda x: float(x.replace('%', ''))/100)
		if 'price_after_perc' in market_files_fixes[f]['fixes']:
			market['prob_after_trade']=market['prob_after_trade'].map(lambda x: float(x.replace('%', ''))/100)
		if 'prob_est_perc' in market_files_fixes[f]['fixes']:
			strperc=market.loc[market['prob_est'].map(type)==str]
			market.loc[market['prob_est'].map(type)==str, 'prob_est']=strperc['prob_est'].map(lambda x: np.nan if x=='no' else float(x.replace('%', ''))/100)
		if 'price_before_100' in market_files_fixes[f]['fixes']:
			market['probability']=market['probability'].map(lambda x: float(x))/100
		if 'price_after_100' in market_files_fixes[f]['fixes']:
			market['prob_after_trade']=market['prob_after_trade'].map(lambda x: float(x))/100
		if 'prob_est_100' in market_files_fixes[f]['fixes']:
			market['prob_est']=market['prob_est'].map(lambda x: float(x))/100
		if 'insert_outcomes' in market_files_fixes[f]['fixes']:
			q_outcomes=questions[['question_id', 'outcome']]
			market=pd.merge(market, q_outcomes, on='question_id', how='inner')
		if 'option_from_stock_name' in market_files_fixes[f]['fixes']:
			q_options=questions[['question_id','options']]
			with_options=pd.merge(market, q_options, on='question_id', how='inner')
			market['answer_option']=with_options[['stock_name', 'options']].apply(get_option_from_options, axis=1)
		if 'team_bad' in market_files_fixes[f]['fixes']:
			market['team_id']=market['team_id'].apply(extract_team)
		if 'with_after_trade' in market_files_fixes[f]['fixes']:
			market.loc[market['prob_after_trade']<=0, 'prob_after_trade']=PROB_MARGIN
			market.loc[market['prob_after_trade']>=1, 'prob_after_trade']=1-PROB_MARGIN
		if 'with_prob_est' in market_files_fixes[f]['fixes']:
			market.loc[market['prob_est']<=0, 'prob_est']=PROB_MARGIN
			market.loc[market['prob_est']>=1, 'prob_est']=1-PROB_MARGIN
		if 'without_team_id' in market_files_fixes[f]['fixes']:
			market=market.assign(team_id=0)

		assert(len(market)>0)
		print(len(market))

		market_forecasts=pd.concat([market_forecasts, market], join='outer')

	# add the some question-specific information to the trades
	qdata=questions.loc[questions['question_id'].isin(market_forecasts['question_id'])][['question_id', 'date_closed', 'date_start', 'date_suspend', 'date_to_close', 'days_open', 'n_opts', 'options', 'q_status', 'q_type']]

	market_forecasts=pd.merge(market_forecasts, qdata, on='question_id', how='inner')

	# prices in (-∞,0]∪[1,∞] are truncated to [MIN_PROB, 1-MIN_PROB]
	market_forecasts.loc[market_forecasts['probability']<=0, 'probability']=PROB_MARGIN
	market_forecasts.loc[market_forecasts['probability']>=1, 'probability']=1-PROB_MARGIN

	market_forecasts['team_id']=pd.to_numeric(market_forecasts['team_id'])

	return market_forecasts

def get_comparable_market_forecasts(files):
	market_forecasts=get_market_forecasts(files)
	market_forecasts=market_forecasts.reindex(columns=comparable_index)

	return market_forecasts

def get_questions():
	questions=pd.DataFrame()

	for f in questions_files:
		questions=pd.concat([questions, pd.read_csv(f)])

	date_fields=['date_start', 'date_suspend', 'date_to_close', 'date_closed']

	for f in date_fields:
		questions[f]=pd.to_datetime(questions[f], dayfirst=True)

	questions=questions.rename(columns={'ifp_id': 'question_id'}, errors="raise")
	questions.loc[:,'question_id']=questions['question_id'].map(simplify_id)
	questions['question_id']=pd.to_numeric(questions['question_id'])

	return questions

def get_survey_forecasts(files):
	survey_forecasts=pd.DataFrame()

	for f in files:
		survey_forecasts=pd.concat([survey_forecasts, pd.read_csv(f)])

	survey_forecasts['timestamp']=pd.to_datetime(survey_forecasts['timestamp'])
	survey_forecasts['fcast_date']=pd.to_datetime(survey_forecasts['fcast_date'])

	survey_forecasts=survey_forecasts.rename(columns={'ifp_id': 'question_id', 'value': 'probability', 'team': 'team_id', 'ctt': 'user_type'}, errors="raise")
	survey_forecasts['q_type']=survey_forecasts['question_id'].apply(extract_type)
	survey_forecasts['question_id']=survey_forecasts['question_id'].apply(extract_id)
	survey_forecasts['question_id']=pd.to_numeric(survey_forecasts['question_id'])

	questions=get_questions()

	survey_forecasts=pd.merge(survey_forecasts, questions, on=['question_id', 'q_type'], suffixes=(None, '_x'))

	survey_forecasts.pop('q_status_x')

	survey_forecasts.loc[survey_forecasts['probability']==0, 'probability']=PROB_MARGIN
	survey_forecasts.loc[survey_forecasts['probability']==1, 'probability']=1-PROB_MARGIN

	survey_forecasts['user_id']=pd.to_numeric(survey_forecasts['user_id'])
	survey_forecasts['team_id']=pd.to_numeric(survey_forecasts['team_id'])

	return survey_forecasts

def get_comparable_survey_forecasts(files):
	survey_forecasts=get_survey_forecasts(files)
	survey_forecasts=survey_forecasts.reindex(columns=comparable_index)

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

def calculate_aggregate_score(forecasts, aggregation_function, scoring_rule, norm=False):
	"""forecasts should be a pandas.DataFrame that contains columns
	question_id, user_id, timestamp, probability, answer_option, outcome, date_closed"""
	res=forecasts.groupby(['question_id', 'answer_option']).apply(apply_aggregation, aggregation_function)
	res.index=res.index.droplevel(['question_id', 'answer_option'])
	if norm:
		res=res.groupby(['question_id']).apply(normalise)
	res=res.groupby(['question_id']).apply(apply_score, scoring_rule)
	res.index=res.index.droplevel(1)
	return res['score']

def apply_aggregation(g, aggregation_function):
	transformed_probs=np.array(aggregation_function(g))
	return pd.DataFrame({'question_id': np.array(g['question_id'])[0], 'probability': transformed_probs, 'outcome': np.array(g['outcome'])[0], 'answer_option': np.array(g['answer_option'])[0]})

def normalise(g):
	Z=np.sum(g['probability'])
	g['probability']=g['probability']/Z
	return g

def apply_score(g, scoring_rule):
	probabilities=np.array(g['probability'])
	outcomes=np.array(g['outcome'])
	options=np.array(g['answer_option'])
	return pd.DataFrame({'score': np.array([scoring_rule(probabilities, outcomes==options)])})

import re
import time
import random
import math
import statistics
import datetime as dt
import numpy as np
import pandas as pd

import general

class ForecastSetBase(general.ForecastSetHandler):
	questions_files=['./data/gjp/ifps.csv']

	def __init__(self, probmargin=0.005):
		super().__init__(probmargin)

	def simplify_id(self, s):
		p=re.compile('^[0-9]+')
		return p.findall(s)[0] if type(s)==str else s

	def extract_id(self, s):
		p=re.compile('^[0-9]+')
		return str(p.findall(s)[0])

	def load_questions(self, questions_files=None):
		if questions_files==None:
			questions_files=self.questions_files
		questions=pd.DataFrame()

		for f in questions_files:
			questions=pd.concat([questions, pd.read_csv(f)])

		date_fields=['date_start', 'date_suspend', 'date_to_close', 'date_closed']

		for f in date_fields:
			questions[f]=pd.to_datetime(questions[f], dayfirst=True)

		questions=questions.rename(columns={'ifp_id': 'question_id'}, errors="raise")
		questions.loc[:,'question_id']=questions['question_id'].map(self.simplify_id)
		questions['question_id']=pd.to_numeric(questions['question_id'], downcast='float')

		self.questions=questions

	def load(self, files=None):
		self.load_complete(files)
		self.forecasts=self.forecasts.reindex(columns=self.comparable_index)

	def load_complete(self, files=None):
		return

class Markets(ForecastSetBase):
	files=['./data/gjp/pm_transactions.lum1.yr2.csv', './data/gjp/pm_transactions.lum2.yr2.csv', './data/gjp/pm_transactions.lum1.yr3.csv', './data/gjp/pm_transactions.lum2a.yr3.csv', './data/gjp/pm_transactions.lum2.yr3.csv', './data/gjp/pm_transactions.inkling.yr3.csv', './data/gjp/pm_transactions.control.yr4.csv', './data/gjp/pm_transactions.batch.train.yr4.csv', './data/gjp/pm_transactions.batch.notrain.yr4.csv', './data/gjp/pm_transactions.supers.yr4.csv', './data/gjp/pm_transactions.teams.yr4.csv']

	year2_default_changes={
		'fixes': ['timestamp', 'price_before_100', 'question_id_str', 'without_team_id', 'insert_outcomes', 'remove_voided', 'conditional_options_a'],
		'column_rename': {
			'IFPID': 'question_id',
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
		'fixes': ['timestamp', 'price_before_100', 'price_after_100', 'prob_est_100', 'question_id_str', 'with_prob_est', 'without_team_id', 'insert_outcomes', 'remove_voided', 'conditional_options_a'],
		'column_rename': {
			'IFPID': 'question_id',
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

	fixes={
		'./data/gjp/pm_transactions.lum1.yr2.csv': year2_default_changes,
		'./data/gjp/pm_transactions.lum2.yr2.csv': year2_default_changes,
		'./data/gjp/pm_transactions.lum1.yr3.csv': year3_default_changes,
		'./data/gjp/pm_transactions.lum2a.yr3.csv': year3_default_changes,
		'./data/gjp/pm_transactions.lum2.yr3.csv': {
			'fixes': ['timestamp', 'price_before_100', 'prob_est_100', 'question_id_str', 'team_bad', 'with_after_trade', 'insert_outcomes', 'with_prob_est', 'remove_voided', 'conditional_options_a'],
			'column_rename': {
				'IFPID': 'question_id',
				'Outcome': 'answer_option',
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
			'fixes': ['timestamp', 'created_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'id_by_name', 'option_from_stock_name', 'with_after_trade', 'with_prob_est', 'without_team_id', 'insert_outcomes', 'remove_voided', 'conditional_options_a'],
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
			'fixes': ['timestamp', 'created_date_us', 'price_before_perc', 'price_after_perc', 'prob_est_perc', 'question_id_str', 'id_in_name', 'insert_outcome', 'option_from_stock_name', 'with_after_trade', 'with_prob_est', 'insert_outcomes'],
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

	def __init__(self, probmargin=0.005):
		super().__init__(probmargin)

	def extract_team(self, s):
		if s=='DEFAULT':
			return 0 # team ID 0 has not been given.
		p=re.compile('e([0-9]{1,2})$')
		return int(p.findall(s)[0])

	# the data has trades on markets, stock names (sn) are possibly substrings
	# of the options, preceded by the name of the option [a-e].
	# yeah, i don't know why anyone would do this either.

	def get_option_from_options(self, t):
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

	def load_complete(self, files=None):
		if files==None:
			files=self.files

		forecasts=pd.DataFrame()

		self.load_questions()
		questions=self.questions.loc[self.questions['q_status']!='voided']
		voidedquestions=self.questions.loc[self.questions['q_status']=='voided'][['q_type', 'question_id']]

		for f in files:
			market=pd.read_csv(f)
			market=market.rename(columns=self.fixes[f]['column_rename'], errors='raise')

			#We want to use question_id below, but we want it to
			#have the correct type already, so sometimes we have to
			#generate it from other data.
			if 'id_by_name' in self.fixes[f]['fixes']:
				q_texts=questions[['question_id','q_text']]
				market=pd.merge(market, q_texts, left_on='market_name', right_on='q_text', how='inner')
				market.pop('q_text')
			if 'id_in_name' in self.fixes[f]['fixes']:
				market['question_id']=market['market_name'].map(self.extract_id)

			market['question_id']=pd.to_numeric(market['question_id'])

			if 'created_date_us' in self.fixes[f]['fixes']:
				market['created_at']=pd.to_datetime(market['created_at'], dayfirst=True)
			if 'timestamp' in self.fixes[f]['fixes']:
				market['timestamp']=pd.to_datetime(market['timestamp'], dayfirst=True)
			if 'price_before_perc' in self.fixes[f]['fixes']:
				market['probability']=market['probability'].map(lambda x: float(x.replace('%', ''))/100)
			if 'price_after_perc' in self.fixes[f]['fixes']:
				market['prob_after_trade']=market['prob_after_trade'].map(lambda x: float(x.replace('%', ''))/100)
			if 'prob_est_perc' in self.fixes[f]['fixes']:
				strperc=market.loc[market['prob_est'].map(type)==str]
				market.loc[market['prob_est'].map(type)==str, 'prob_est']=strperc['prob_est'].map(lambda x: np.nan if x=='no' else float(x.replace('%', ''))/100)
			if 'price_before_100' in self.fixes[f]['fixes']:
				market['probability']=market['probability'].map(lambda x: float(x))/100
			if 'price_after_100' in self.fixes[f]['fixes']:
				market['prob_after_trade']=market['prob_after_trade'].map(lambda x: float(x))/100
			if 'prob_est_100' in self.fixes[f]['fixes']:
				market['prob_est']=market['prob_est'].map(lambda x: float(x))/100
			if 'insert_outcomes' in self.fixes[f]['fixes']:
				q_outcomes=questions[['question_id', 'outcome']]
				market=pd.merge(market, q_outcomes, on='question_id', how='inner')
			if 'option_from_stock_name' in self.fixes[f]['fixes']:
				q_options=questions[['question_id','options']]
				with_options=pd.merge(market, q_options, on='question_id', how='inner')
				market['answer_option']=with_options[['stock_name', 'options']].apply(self.get_option_from_options, axis=1)
			if 'team_bad' in self.fixes[f]['fixes']:
				market['team_id']=market['team_id'].apply(self.extract_team)
			if 'with_after_trade' in self.fixes[f]['fixes']:
				market.loc[market['prob_after_trade']<=0, 'prob_after_trade']=self.probmargin
				market.loc[market['prob_after_trade']>=1, 'prob_after_trade']=1-self.probmargin
			if 'with_prob_est' in self.fixes[f]['fixes']:
				market.loc[market['prob_est']<=0, 'prob_est']=self.probmargin
				market.loc[market['prob_est']>=1, 'prob_est']=1-self.probmargin
			if 'without_team_id' in self.fixes[f]['fixes']:
				market=market.assign(team_id=0)
			# On conditional markets, the answer option refers to the branch
			# of the conditional market ('a' is the first market
			# (-1), 'b' is the second market (-2), etc. Don't
			# ask, I didn't make this up). Therefore, we here
			# have to remove forecasts on voided questions
			# from the dataset.  Furthermore, the answer on
			# the non-voided conditional market is always
			# assumed to be "a", so we have to insert it.
			if 'remove_voided' in self.fixes[f]['fixes']:
				# We assume that the answer_option designates the branch
				market['q_type']=market['answer_option'].apply(lambda x: x.encode()[0]-('a'.encode()[0]-1))
				# We remove the forecasts on voided questions
				# from the dataset by first outer joining the forecasts
				# and the voided questions, and then removing
				# rows where both occurred.
				market=pd.merge(market, voidedquestions, on=['q_type', 'question_id'], how='outer', indicator=True)
				market=market[~((market['_merge']=='both')|(market['_merge']=='right_only'))].drop('_merge', axis=1)
				market=market.drop(['q_type'], axis=1)
			# Since the field 'answer_option' on conditional prediction markets
			# refers to the branch of the market (as per personal communication from
			# the GJOpen team), the default answer for prices
			# on conditional markets in 'a'. We have to set
			# this here.
			if 'conditional_options_a' in self.fixes[f]['fixes']:
				onlytype=questions[['question_id', 'q_type']]
				# this works because the question_ids
				# of onlytype are a superset of the
				# question_ids of questions.
				market=pd.merge(market, onlytype, on=['question_id'], how='inner')
				market.loc[(market['q_type']!=0)&(market['q_type']!=6),'answer_option']='a'
				market=market.drop(['q_type'], axis=1)

			assert(len(market)>0)

			forecasts=pd.concat([forecasts, market], join='outer')

		# add the some question-specific information to the trades
		qdata=questions.loc[questions['question_id'].isin(forecasts['question_id'])][['question_id', 'date_closed', 'date_start', 'date_suspend', 'date_to_close', 'days_open', 'n_opts', 'options', 'q_status', 'q_type']]

		forecasts=pd.merge(forecasts, qdata, on='question_id', how='inner')

		# prices in (-∞,0]∪[1,∞] are truncated to [MIN_PROB, 1-MIN_PROB]
		forecasts.loc[forecasts['probability']<=0, 'probability']=self.probmargin
		forecasts.loc[forecasts['probability']>=1, 'probability']=1-self.probmargin

		forecasts['team_id']=pd.to_numeric(forecasts['team_id'])

		self.forecasts=forecasts

class Surveys(ForecastSetBase):
	files=['./data/gjp/survey_fcasts.yr1.csv', './data/gjp/survey_fcasts.yr2.csv', './data/gjp/survey_fcasts.yr3.csv.zip', './data/gjp/survey_fcasts.yr4.csv.zip']

	def __init__(self, probmargin=0.005):
		super().__init__(probmargin)

	def extract_type(self, s):
		p=re.compile('-([0-6])$')
		return int(p.findall(s)[0])

	def load_complete(self, files=None):
		if files==None:
			files=self.files
		forecasts=pd.DataFrame()

		for f in files:
			forecasts=pd.concat([forecasts, pd.read_csv(f)])

		forecasts['timestamp']=pd.to_datetime(forecasts['timestamp'])
		forecasts['fcast_date']=pd.to_datetime(forecasts['fcast_date'])

		forecasts=forecasts.rename(columns={'ifp_id': 'question_id', 'value': 'probability', 'team': 'team_id', 'ctt': 'user_type'}, errors="raise")
		forecasts['q_type']=forecasts['question_id'].apply(self.extract_type)
		forecasts['question_id']=forecasts['question_id'].apply(self.extract_id)
		forecasts['question_id']=pd.to_numeric(forecasts['question_id'])

		self.load_questions()

		forecasts=pd.merge(forecasts, self.questions, on=['question_id', 'q_type'], suffixes=(None, '_x'))

		forecasts.pop('q_status_x')

		forecasts.loc[forecasts['probability']==0, 'probability']=self.probmargin
		forecasts.loc[forecasts['probability']==1, 'probability']=1-self.probmargin

		forecasts['user_id']=pd.to_numeric(forecasts['user_id'])
		forecasts['team_id']=pd.to_numeric(forecasts['team_id'])

		self.forecasts=forecasts

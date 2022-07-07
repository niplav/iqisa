import re
import time
import random
import math
import statistics
import datetime as dt
import numpy as np
import pandas as pd

class ForecastSetHandler():
	comparable_index=['question_id', 'user_id', 'team_id', 'probability', 'answer_option', 'timestamp', 'outcome', 'date_start', 'date_suspend', 'date_to_close', 'date_closed', 'days_open', 'n_opts', 'options', 'q_status', 'q_type']

	def __init__(self, probmargin=0.005):
		self.probmargin=probmargin
		self.with_cumul_scores=False
		self.time_frontfilled=False
		self.forecasts=pd.DataFrame()
		self.questions=pd.DataFrame()
		self.aggregations=pd.DataFrame()
		self.scores=pd.DataFrame()

	def aggregate(self, aggregation_function, *args):
		"""forecasts should be a pandas.DataFrame that contains columns
		question_id, user_id, timestamp, probability, answer_option, outcome, date_closed"""
		self.aggregations=self.forecasts.groupby(['question_id', 'answer_option']).apply(self.apply_aggregation, aggregation_function, *args)
		self.aggregations.index=self.aggregations.index.droplevel(['question_id', 'answer_option'])

	def apply_aggregation(self, g, aggregation_function, *args):
		transformed_probs=np.array(aggregation_function(g, *args))
		return pd.DataFrame({'question_id': np.array(g['question_id'])[0], 'probability': transformed_probs, 'outcome': np.array(g['outcome'])[0], 'answer_option': np.array(g['answer_option'])[0]})

	# TODO: Move score_aggregations and score onto the same underlying
	# function

	def score_aggregations(self, scoring_rule, *args):
		self.scores=self.aggregations.groupby(['question_id']).apply(self.apply_score_aggr, scoring_rule, *args)
		self.scores.index=self.scores.index.droplevel(1)

	def apply_score_aggr(self, g, scoring_rule, *args):
		probabilities=np.array(g['probability'])
		outcomes=np.array(g['outcome'])
		options=np.array(g['answer_option'])
		return pd.DataFrame({'score': np.array([scoring_rule(probabilities, outcomes==options, *args)])})

	def score(self, scoring_rule, *args):
		if len(self.forecasts)==0:
			raise Exception('no forecasts loaded yet, use .load()')
		self.scores=self.forecasts.groupby(['question_id']).apply(self.apply_score, scoring_rule, *args)
		self.scores.index=self.scores.index.droplevel(1)

	def apply_score(self, g, scoring_rule, *args):
		probabilities=np.array(g['probability'])
		outcomes=np.array(g['outcome'])
		options=np.array(g['answer_option'])
		return pd.DataFrame({'score': np.array([scoring_rule(probabilities, outcomes==options, *args)])})

	def normalise(self):
		if len(self.aggregations)==0:
			raise Exception('no forecasts aggregated yet, use .aggregate()')
		self.aggregations=self.aggregations.groupby(['question_id']).apply(self.normalise)

	def apply_normalise(self, g):
		Z=np.sum(g['probability'])
		g['probability']=g['probability']/Z
		return g

	# This function can't be written in a pandastic way because
	# expanding.Expanding.apply only accepts single columns (yes, even with
	# numba). I hope future versions will allow for a version of apply that
	# plays nicely with expanding. Perhaps I'll find the time to write it.
	# Also, it is _slow_: 110 seconds for the 254598 rows of market data
	# from the last 2 years.

	def add_cumul_user_score(self, scoring_rule, *args):
		self.forecasts=self.forecasts.groupby(['user_id']).apply(self.cumul_score, scoring_rule, *args)
		self.forecasts=self.forecasts.reset_index(drop=True)
		self.with_cumul_scores=True

	def cumul_score(self, g, scoring_rule, *args):
		g=g.sort_values('date_suspend')
		fst=g.index[0]
		cumul_scores=[]
		for lim in g.index:
			expan=g.loc[fst:lim,:]
			cumul_scores.append(scoring_rule(expan['probability'], expan['answer_option']==expan['outcome'], *args))
		g['cumul_score']=np.array(cumul_scores)
		return g

	# TODO: Maybe make this a tiny bit faster
	# Idea: keep resbef, only expand it if necessary, have user_scores
	# precomputed as well, only update it if resbef has changed (and if so,
	# only with the new resbef values).

	def add_cumul_user_perc(self, lower_better=True):
		if not self.with_cumul_scores:
			raise Exception('cumulative scores not set')
		self.forecasts=self.forecasts.sort_values('timestamp')
		fst=self.forecasts.index[0]
		cumul_rankings=[]
		for lim in self.forecasts.index:
			expan=self.forecasts.loc[fst:lim,:]
			#timestamp of current forecast
			cur=self.forecasts.loc[lim:lim,:]
			curts=cur['timestamp'].values[0]
			#get the self.forecasts that have resolved before the current forecast happened
			resbef=expan.loc[expan['date_suspend']<curts]
			#get the score of the last resolved forecast each forecaster made before the current forecast
			user_scores=resbef.groupby(['user_id'])['cumul_score'].last()
			user_scores=np.sort(user_scores)
			curscore=cur['cumul_score'].values[0]
			if len(user_scores)==0:
				# by default assume the user is average
				percentile=0.5
			else:
				if lower_better:
					percentile=len(user_scores[user_scores>=curscore])/len(user_scores)
				else:
					percentile=len(user_scores[user_scores<=curscore])/len(user_scores)
			assert(0<=percentile<=1)
			cumul_rankings.append(percentile)
		self.forecasts['cumul_perc']=np.array(cumul_rankings)

	def frontfill_forecasts(self):
		"""forecasts should be a dataframe with at least these five fields:
		question_id, user_id, timestamp, probability"""
		if len(self.forecasts)==0:
			raise Exception('no forecasts loaded yet, use .load()')

		self.forecasts=self.forecasts.groupby(['question_id', 'user_id', 'answer_option']).apply(self.frontfill_group)
		self.forecasts.index=self.forecasts.index.droplevel(['question_id', 'user_id', 'answer_option'])
		self.time_frontfilled=True

	def frontfill_group(self, g):
		"""warning: this makes the forecast ids useless"""
		dates=pd.date_range(start=min(g.timestamp), end=max(g.date_closed), freq='D')
		alldates=pd.DataFrame({'timestamp': dates})
		g=g.merge(alldates, on='timestamp', how='outer')
		g=g.sort_values(by='timestamp')
		g['timestamp']=g['timestamp'].fillna(g['timestamp'])
		g=g.fillna(method='ffill')
		return g

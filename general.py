import re
import time
import random
import math
import statistics
import datetime as dt
import numpy as np
import pandas as pd

def frontfill_forecasts(forecasts):
	"""forecasts should be a dataframe with at least these five fields:
	question_id, user_id, timestamp, probability"""
	res=forecasts.groupby(['question_id', 'user_id', 'answer_option']).apply(frontfill_group)
	res.index=res.index.droplevel(['question_id', 'user_id', 'answer_option'])
	return res

def frontfill_group(g):
	"""warning: this makes the forecast ids useless"""
	dates=pd.date_range(start=min(g.timestamp), end=max(g.date_closed), freq='D')
	alldates=pd.DataFrame({'timestamp': dates})
	g=g.merge(alldates, on='timestamp', how='outer')
	g=g.sort_values(by='timestamp')
	g['timestamp']=g['timestamp'].fillna(g['timestamp'])
	g=g.fillna(method='ffill')
	return g

def aggregate(forecasts, aggregation_function, *args):
	"""forecasts should be a pandas.DataFrame that contains columns
	question_id, user_id, timestamp, probability, answer_option, outcome, date_closed"""
	res=forecasts.groupby(['question_id', 'answer_option']).apply(apply_aggregation, aggregation_function, *args)
	res.index=res.index.droplevel(['question_id', 'answer_option'])
	return res

def apply_aggregation(g, aggregation_function, *args):
	transformed_probs=np.array(aggregation_function(g, *args))
	return pd.DataFrame({'question_id': np.array(g['question_id'])[0], 'probability': transformed_probs, 'outcome': np.array(g['outcome'])[0], 'answer_option': np.array(g['answer_option'])[0]})

def normalise(forecasts):
	return forecasts.groupby(['question_id']).apply(normalise)

def apply_normalise(g):
	Z=np.sum(g['probability'])
	g['probability']=g['probability']/Z
	return g

def score(aggr_forecasts, scoring_rule, *args):
	res=aggr_forecasts.groupby(['question_id']).apply(apply_score, scoring_rule, *args)
	res.index=res.index.droplevel(1)
	return res['score']

def apply_score(g, scoring_rule, *args):
	probabilities=np.array(g['probability'])
	outcomes=np.array(g['outcome'])
	options=np.array(g['answer_option'])
	return pd.DataFrame({'score': np.array([scoring_rule(probabilities, outcomes==options, *args)])})

# This function can't be written in a pandastic way because
# expanding.Expanding.apply only accepts single columns (yes, even with
# numba). I hope future versions will allow for a version of apply that
# plays nicely with expanding. Perhaps I'll find the time to write it.
# Also, it is _slow_: 110 seconds for the 254598 rows of market data
# from the last 2 years.

def cumul_user_score(forecasts, scoring_rule, *args):
	user_perf=forecasts.groupby(['user_id']).apply(cumul_score, scoring_rule, *args)
	user_perf=user_perf.reset_index(drop=True)
	return user_perf

def cumul_score(g, scoring_rule, *args):
	g=g.sort_values('date_suspend')
	fst=g.index[0]
	cumul_scores=[]
	for lim in g.index:
		expan=g.loc[fst:lim,:]
		cumul_scores.append(scoring_rule(expan['probability'], expan['answer_option']==expan['outcome'], *args))
	g['cumul_score']=np.array(cumul_scores)
	return g

# Maybe make this a tiny bit faster
# Idea: keep resbef, only expand it if necessary, have user_scores
# precomputed as well, only update it if resbef has changed (and if so,
# only with the new resbef values).

def cumul_user_perc(forecasts, lower_better=True):
	forecasts=forecasts.sort_values('timestamp')
	fst=forecasts.index[0]
	cumul_rankings=[]
	for lim in forecasts.index:
		expan=forecasts.loc[fst:lim,:]
		#timestamp of current forecast
		cur=forecasts.loc[lim:lim,:]
		curts=cur['timestamp'].values[0]
		#get the forecasts that have resolved before the current forecast happened
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
	forecasts['cumul_perc']=np.array(cumul_rankings)
	return forecasts

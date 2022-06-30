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

def aggregate(forecasts, aggregation_function, *args, norm=False):
	"""forecasts should be a pandas.DataFrame that contains columns
	question_id, user_id, timestamp, probability, answer_option, outcome, date_closed"""
	res=forecasts.groupby(['question_id', 'answer_option']).apply(apply_aggregation, aggregation_function, *args)
	res.index=res.index.droplevel(['question_id', 'answer_option'])
	if norm:
		res=res.groupby(['question_id']).apply(normalise)
	return res

def apply_aggregation(g, aggregation_function, *args):
	transformed_probs=np.array(aggregation_function(g, *args))
	return pd.DataFrame({'question_id': np.array(g['question_id'])[0], 'probability': transformed_probs, 'outcome': np.array(g['outcome'])[0], 'answer_option': np.array(g['answer_option'])[0]})

def normalise(g):
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

def add_past_user_performance(forecasts, scoring_rule):
	return forecasts

import numpy as np

def arith_aggr(forecasts):
	return np.array([np.mean(forecasts['probability'])])

def geom_aggr(forecasts):
	return np.array([statistics.geometric_mean(forecasts['probability'])])

def brier_score(probabilities, outcomes):
	return np.mean((probabilities-outcomes)**2)

def usuniq(l):
	r=[]
	nanfound=False
	for e in l:
		if type(e)==float:
			if np.isnan(e) and nanfound:
				continue
			if np.isnan(e) and not nanfound:
				nanfound=True
				r.append(e)
		if e in r:
			continue
		r.append(e)
	return r

def both(cn):
	print(usuniq(market_forecasts[cn]))
	print(usuniq(survey_forecasts[cn]))

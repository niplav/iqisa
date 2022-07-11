import gjp
import general

import math
import itertools
import statistics
import numpy as np

def arith_aggr(forecasts, *args):
	return np.array([np.mean(forecasts['probability'])])

def geom_aggr(forecasts, *args):
	return np.array([statistics.geometric_mean(forecasts['probability'])])

def brier_score(probabilities, outcomes, *args):
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

class Aggregator:
	def __init__(self):
		self.aggr_methods=[]
		self.aggr_index=0
		self.extr=3
		means=['arith', 'geom', 'median']
		formats=['probs', 'odds', 'logodds']
		decay=['nodec', 'dec']
		expertise=['noexp', 'exp']
		extremize=['gjpextr', 'postextr', 'neyextr', 'befextr', 'noextr']
		for e in itertools.product(means, formats, decay, expertise, extremize):
			#the first sometimes doesn't work (negative values)
			#the second is equivalent to the geometric mean of odds
			#I also don't know how to compute the weighted geometric mean/median
			if (e[0]=='geom' and e[1]=='logodds') or (e[0]=='arith' and e[1]=='logodds') or (e[2]=='dec' and e[0]!='arith'):
				continue
			self.aggr_methods.append(e)

	def all_aggregations(self, forecasts, norm=False):
		self.aggr_index=0
		self.compute_user_performance(forecasts)
		results=dict()

		for i in range(0, len(self.aggr_methods)):
			res=gjp.calculate_aggregate_score(forecasts, self.aggregate, brier_score, norm=norm)
			res=np.mean(res)
			results['_'.join(self.aggr_methods[self.aggr_index])]=res
			print(self.aggr_methods[self.aggr_index], res)
			self.aggr_index+=1

		results=[(results[k], k) for k in results.keys()]
		results.sort()

		return results

#survey_forecasts=gjp.get_comparable_survey_forecasts(gjp.survey_files)
#team_forecasts=survey_forecasts.loc[survey_forecasts['team_id'].notna()]
#nonteam_forecasts=survey_forecasts.loc[survey_forecasts['team_id'].isna()]
market_forecasts=gjp.get_comparable_market_forecasts(gjp.broken_market_files)
#mini_survey=gjp.get_comparable_survey_forecasts(['data/gjp/survey_fcasts_mini.yr1.csv'])

# broken: 2,3,4
# seriously broken: 2,3,4

#a=Aggregator()

#print('all surveys:')
#a.all_aggregations(survey_forecasts)
#
#print('surveys teams:')
#a.all_aggregations(team_forecasts)
#
#print('surveys non-teams:')
#a.all_aggregations(nonteam_forecasts)
#
#print('all markets non-teams:')
#a.all_aggregations(market_forecasts)

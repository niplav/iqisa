import json
import time

import numpy as np
import pandas as pd

import iqisa

class PrivateBinary(iqisa.ForecastSetHandler):
	def load(self, files):
		self.load_complete(files)

	def load_complete(self, files):
		f=open(files)
		jsondata=json.load(f)

		user_ids=[]
		team_ids=[]
		probabilities=[]
		answer_options=[]
		timestamps=[]
		outcomes=[]
		open_times=[]
		resolve_times=[]

		for question in jsondata:
			if question['question_type']=='binary':
				resolution=str(question['resolution'])
				open_time=pd.to_datetime(question['publish_time'])
				resolve_time=pd.to_datetime(question['resolve_time'])
				numf=0
				for forecast in question['prediction_timeseries']:
					user_ids.append(int(forecast['user_id']))
					probabilities.append(float(forecast['prediction']))
					timestamps.append(pd.to_datetime(forecast['timestamp']))
					numf+=1
				open_times+=[open_time]*numf
				resolve_times+=[resolve_time]*numf
				outcomes+=[resolution]*numf
		numf=len(probabilities)
		answer_options=['1']*numf
		outcomes=['1']*numf
		team_ids=[0]*numf
		n_opts=[2]*numf
		options=['(0) No, (1) Yes']*numf
		q_status=['resolved']*numf
		q_type=[0]*numf

		self.forecasts=pd.DataFrame({'user_id': user_ids, 'team_id': team_ids, 'probability': probabilities, 'answer_option': answer_options, 'timestamp': timestamps, 'outcome': outcomes, 'open_time': open_times, 'resolve_time': resolve_times, 'n_opts': n_opts, 'options': options, 'q_status': q_status, 'q_type': q_type})

	def load_questions(self, files):
		return
		# TODO: do stuff

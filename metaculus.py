import json
import time

import numpy as np
import pandas as pd

import iqisa

comparable_index=['question_id', 'user_id', 'team_id', 'probability', 'answer_option', 'timestamp', 'outcome', 'open_time', 'date_suspend', 'date_to_close', 'date_closed', 'days_open', 'n_opts', 'options', 'q_status', 'q_type']

class PrivateBinary(iqisa.ForecastSetHandler):
	def load(self, files):
		self.load_complete(files)

	def load_complete_1(self, files):
		self.forecasts=pd.DataFrame(columns=comparable_index)
		f=open(files)
		jsondata=json.load(f)
		for question in jsondata:
			if question['question_type']=='binary':
				resolution=str(question['resolution'])
				open_time=pd.to_datetime(question['publish_time'])
				resolve_time=pd.to_datetime(question['resolve_time'])
				user_ids=[]
				probabilities=[]
				timestamps=[]
				for forecast in question['prediction_timeseries']:
					user_ids.append(int(forecast['user_id']))
					probabilities.append(float(forecast['prediction']))
					timestamps.append(pd.to_datetime(forecast['timestamp']))
				numf=len(probabilities)
				newrows=pd.DataFrame({'user_id': user_ids, 'team_id': np.repeat([0], numf), 'probability': probabilities, 'answer_option': np.repeat(['1'], numf), 'timestamp': timestamps, 'outcome': np.repeat([resolution], numf), 'open_time': np.repeat([open_time], numf), 'resolve_time': np.repeat([resolve_time], numf)})
				self.forecasts=self.forecasts.append(newrows)

	def load_complete(self, files):
		self.forecasts=pd.DataFrame(columns=comparable_index)
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

		self.forecasts=pd.DataFrame({'user_id': user_ids, 'team_id': team_ids, 'probability': probabilities, 'answer_option': answer_options, 'timestamp': timestamps, 'outcome': outcomes, 'open_time': open_times, 'resolve_time': resolve_times})

	def load_questions(self, files):
		return
		# TODO: do stuff

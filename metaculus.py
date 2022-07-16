import json
import time

import datetime as dt
import numpy as np
import pandas as pd

import iqisa

class PrivateBinary(iqisa.ForecastSetHandler):
	question_data_file='./data/metaculus/questions.json'
	def load(self, data_file):
		self.load_complete(data_file)

	def load_complete(self, data_file):
		f=open(data_file)
		jsondata=json.load(f)

		user_ids=[]
		team_ids=[]
		probabilities=[]
		answer_options=[]
		timestamps=[]
		outcomes=[]
		open_times=[]
		resolve_times=[]
		question_titles=[]

		for question in jsondata:
			if question['question_type']=='binary':
				resolution=str(question['resolution'])
				open_time=pd.to_datetime(question['publish_time'])
				resolve_time=pd.to_datetime(question['resolve_time'])
				question_title=str(question['question_title'])
				numf=0
				for forecast in question['prediction_timeseries']:
					user_ids.append(int(forecast['user_id']))
					probabilities.append(float(forecast['prediction']))
					timestamps.append(pd.to_datetime(forecast['timestamp']))
					numf+=1
				open_times+=[open_time]*numf
				resolve_times+=[resolve_time]*numf
				outcomes+=[resolution]*numf
				question_titles+=[resolution]*numf
		numf=len(probabilities)
		answer_options=['1']*numf
		outcomes=['1']*numf
		team_ids=[0]*numf
		n_opts=[2]*numf
		options=['(0) No, (1) Yes']*numf
		q_status=['resolved']*numf
		q_type=[0]*numf

		self.forecasts=pd.DataFrame({'user_id': user_ids, 'team_id': team_ids, 'probability': probabilities, 'answer_option': answer_options, 'timestamp': timestamps, 'outcome': outcomes, 'open_time': open_times, 'resolve_time': resolve_times, 'n_opts': n_opts, 'options': options, 'q_status': q_status, 'q_type': q_type})

	def load_questions(self, data_file=None):
		if data_file==None:
			data_file=self.question_data_file
		f=open(data_file)
		jsondata=json.load(f)

		question_ids=[]
		open_times=[]
		close_times=[]
		resolve_times=[]
		outcomes=[]
		question_titles=[]
		question_statuses=[]

		for question in jsondata:
			question_ids.append(int(question['question_id']))
			open_times.append(pd.to_datetime(question['open_time']))
			# without the coerce this would sometimes fail
			# because for Metaculus data some resolution times
			# are outside the 64-bit nanosecond representable
			# timescale
			# TODO: Fix by switching to python datetime
			# instead of pandas datetime
			close_time=pd.to_datetime(question['close_time'], errors='coerce')
			close_times.append(close_time)
			resolve_times.append(pd.to_datetime(question['resolve_time'], errors='coerce'))
			if question['outcome']==None or question['outcome']==-1:
				outcomes.append(np.nan)
			else:
				outcomes.append(str(question['outcome']))
			question_titles.append(question['question_title'])

			if question['outcome']==None:
				# I don't see the data giving any better indication of
				# whether the question has closed
				# TODO: think about this with a Yoda timer?
				now=pd.to_datetime(dt.datetime.utcnow(), utc=True)
				if now>close_time:
					question_statuses.append('closed')
				else:
					question_statuses.append('open')
			elif question['outcome']==-1:
				question_statuses.append('voided')
			else:
				question_statuses.append('resolved')

		self.questions=pd.DataFrame({'question_id': question_ids, 'q_title': question_titles, 'open_time': open_times, 'close_time': close_times, 'resolve_time': resolve_times, 'outcome': outcomes, 'q_status': question_statuses})

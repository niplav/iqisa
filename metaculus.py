import json
import time

import numpy as np
import pandas as pd

import general

class PrivateBinary(general.ForecastSetHandler):
	def __init__(self, probmargin=0.005):
		super.__init__(probmargin)

	def load(self, files):
		self.forecasts=pd.DataFrame()

	def load_complete(self, files):
		self.forecasts=pd.DataFrame()
		f=open(files)
		jsondata=json.load(f)
		for question in jsondata:
			if question["question_type"]=="binary":
				return
				# TODO: do stuff

	def load_questions(self, files):
		return
		# TODO: do stuff

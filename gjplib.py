import time
import random
import math
import datetime as dt
import numpy as np
import pandas as pd

PROB_MARGIN=0.005

survey_files=["./survey_fcasts.yr1.csv", "./survey_fcasts.yr2.csv", "./survey_fcasts.yr3.csv", "./survey_fcasts.yr4.csv"]
questions_files=["ifps.csv"]

def get_questions():
	questions=pd.DataFrame()

	for f in questions_files:
		questions=pd.concat([questions, pd.read_csv(f)])

	date_fields=['date_start', 'date_suspend', 'date_to_close', 'date_closed']

	for f in date_fields:
		questions[f]=pd.to_datetime(questions[f], dayfirst=True)

	return questions

def get_survey_forecasts():
	survey_forecasts=pd.DataFrame()

	for f in survey_files:
		survey_forecasts=pd.concat([survey_forecasts, pd.read_csv(f)])

	survey_forecasts['timestamp']=pd.to_datetime(survey_forecasts['timestamp'])

	questions=get_questions()
	survey_forecasts=pd.merge(survey_forecasts, questions, on='ifp_id')

	unnecessary_columns=['q_text', 'q_desc', 'short_title', 'options', 'fcast_date']

	for c in unnecessary_columns:
		survey_forecasts.pop(c)

	survey_forecasts.rename(columns={'ifp_id': 'question_id', 'value': 'forecast'}, errors="raise") # Y U NO WORK‽

	survey_forecasts.loc[survey_forecasts['value']==0, 'value']=PROB_MARGIN
	survey_forecasts.loc[survey_forecasts['value']==1, 'value']=1-PROB_MARGIN

	return survey_forecasts

def backfill_forecasts(forecasts):
	"""forecasts should be a dataframe with at least these five fields:
	question_id, user_id, timestamp, value, date_closed"""
	return

import gjp

m=gjp.Markets()
s=gjp.Surveys()

m.load()
s.load()

m.forecasts.loc[(m.forecasts['question_id']==1040)&(m.forecasts['answer_option']=='a')&(m.forecasts['user_id']==6203)&(m.forecasts['probability']==0.45)]

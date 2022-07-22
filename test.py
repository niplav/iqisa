import gjp

m=gjp.load_markets()
s=gjp.load_surveys()

m.loc[(m['question_id']==1040)&(m['answer_option']=='a')&(m['user_id']==6203)&(m['probability']==0.45)]

import pandas as pd
import numpy as np

hours=pd.read_csv("hours.csv")

hours['start']=pd.to_datetime(hours['start'])
hours['end']=pd.to_datetime(hours['end'])
print(np.sum(hours['end']-hours['start']))

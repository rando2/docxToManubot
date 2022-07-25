import pandas as pd
from sklearn.linear_model import LinearRegression
from plydata import *

# need these for use in plydata (not detected as used by IDE)
import numpy as np
from scipy.stats import zscore

def calcReg(x, y):
    # Draw an identity line capturing max score indices based on row number
    data = pd.DataFrame(data=y, index=x).dropna()
    model = LinearRegression().fit(pd.DataFrame(data.index), pd.DataFrame(data["y"]))
    return model.predict(pd.DataFrame(x))

# Load the scores from the heatmap
heatmap = pd.read_csv("heatmap.csv", index_col=None)

# Identify the best match for each row
max_pos = pd.DataFrame({'max_col': pd.to_numeric(heatmap.T.idxmax(), errors='ignore')})
                       #'max_val': pd.to_numeric(heatmap.T.max(), errors='ignore')})
max_pos.index = pd.to_numeric(max_pos.index, errors='ignore')

# Clean up outliers & non-monotonic changes (max_col is always first max, so should be biased
# towards lower numbers)
# Then predict the where best match will fall using linear regression, then identify places with exact or
# very close matches
max_pos = max_pos \
          >> define(row = max_pos.index.astype("int"), diff='max_col - max_col.shift(1)')\
          >> define(z='zscore(diff, nan_policy="omit")')\
          >> define(y=if_else('(z >= 2)', 'np.nan', 'max_col'))\
          >> define(prediction='calcReg(row, y)')\
          >> define(match=if_else('y == np.floor(prediction)', 'np.floor(prediction)',
                                      if_else('y == np.ceil(prediction)', 'np.ceil(prediction)', -1)))\
          >> select("row", "max_col", "y", "prediction", "match")

# Manually set first and last to ensure all data is included
max_pos.at[0, "match"] = 0
max_pos.at[len(max_pos.index)-1, "match"] = len(heatmap.columns) - 1

# Iteratively update the matches where monotonic, nearly-linear increase is detected
update = max_pos >> query('match == -1') >> count()
prev = max_pos >> count()
prev = prev.values[0][0]
while update.values[0][0] < prev :
    prev = update.values[0][0]
    max_pos = max_pos \
              >> define(match=if_else('(match == -1) & (prediction.astype("int") == prediction.shift(1) + 1)',
                                      'match.shift(1) + 1',
                                      if_else('(match == -1) & (prediction.astype("int") == prediction.shift(-1) - 1)',
                                              'match.shift(-1) - 1', 'match')))\
              >> define(match=if_else('(match == -1) & (match.shift(1) + 1 == max_col)',
                                      'match.shift(1) + 1', 'match')) \
              >> define(match=if_else('(match == -1) & (match.shift(-1) - 1 == max_col)',
                                      'match.shift(-1) - 1', 'match'))\
              >> define(match=if_else(('(match == -1) & (match.shift(1) != -1) & (match.shift(1) + 1 == max_col)'),
                                      'match.shift(1) + 1',
                                      'match'))\
              >> define(match=if_else(('(match == -1) & (match.shift(1) != -1) & (match.shift(-1) != -1) &'
                                      '(match.shift(1) + 2 == match.shift(-1))'),
                                      'match.shift(1) + 1',
                                      'match')) \
              >> define(match=if_else(('(match == -1) & (match.shift(1) != -1) & ((match.shift(1) == match.shift(-1))'
                                       '| (match.shift(1) + 1 == match.shift(-1)))'),
                                      'match.shift(1)',
                                      'match')) \
              >> define(match=if_else('(match == -1) & ((max_col == max_col.shift(1) + 1) | (max_col == max_col.shift(-1) - 1))',
                                      'max_col', 'match')) \
              >> define(prediction2=if_else('(match == -1) & (match.shift(1) != -1)',
                                          'prediction + (match.shift(1) - prediction.shift(1))',
                                          'prediction'))\
              >> define(match=if_else('(match == -1)',
                                         if_else('max_col == np.floor(prediction2)',
                                                 'np.floor(prediction2)',
                                                 if_else('max_col == np.ceil(prediction2)',
                                                         'np.ceil(prediction2)',
                                                         -1)),
                                         'match')) \
              >> define(match=if_else('(match != -1) & (match < match.shift(1))',
                                      -1, 'match')) # correct any that are not monotonic

    update = max_pos \
             >> query('match == -1')\
             >> count()

print(max_pos.iloc[20:30,])
max_pos.to_csv("tmp/max.csv", index=False)
exit(0)
exit(0)
# Handle remaining blank predictions
undefined = max_pos \
            >> define(last= 'match.shift(1)', next= 'match.shift(-1)')\
            >> query("match == -1")\
            >> select("row", "max_col", "prediction", "y", "last", "next")

if len(undefined.index) > 0:
    print(undefined)
    exit("missing some assignments")

max_pos = max_pos \
          >> define(match='match.astype(int)')\
          >> select("match")

max_pos.to_csv("tmp/max.csv")

import pandas as pd
import numpy as np
from plotnine import *
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from plydata import tidy
from plydata import *

def calcReg(x, y):
    # Draw an identity line capturing max score indices based on row number
    data = pd.DataFrame(data=y, index=x).dropna()
    model = LinearRegression().fit(pd.DataFrame(data.index), pd.DataFrame(data["y"]))
    return model.predict(pd.DataFrame(x))

def checkModel(df, groupNum = 0):
    match = list()
    unmatched = list()
    for i in range(df.index.min(), df.index.max()+1):  # for each row
        if df["max_col"][i] == np.floor(df["prediction"][i]) or \
                df["max_col"][i] == np.ceil(df["prediction"][i]):

            # First, back fill if the last cell couldn't be identified, but the trend is evident
            if len(match) >= 2 and match[-1] == -1 and match[-2] != -1:
                if match[-2] + 2 == df["max_col"][i]:
                    # if line can be drawn
                    match[-1] = df["max_col"][i] - 1
                    unmatched[-1] = None
                elif match[-2] + 1 == df["max_col"][i]:
                    # if last cell should be stuck onto one of these cells
                    match[-1] = df["max_col"][i-2]
                    unmatched[-1] = None

            # Then, add info for this match
            match.append(df["max_col"][i])
            unmatched.append(None)
        else:
            match.append(-1)
            if len(unmatched) > 0 and unmatched[-1] is None:
                groupNum += 1
            unmatched.append(groupNum)
    return match, unmatched, groupNum

def applyChanges(match, unmatch, max_pos):
    for j in range(0, len(match)):
        max_pos.at[priorRow + 1 + j, "match"] = match[j]
        max_pos.at[priorRow + 1 + j, "unmatched"] = unmatch[j]
    return max_pos

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
          >> define(y=if_else('(diff < 0) | (z >= 2)', 'np.nan', 'max_col'))\
          >> define(prediction='calcReg(row, y)')\
          >> define(match=if_else('y == np.floor(prediction)', 'np.floor(prediction)',
                                      if_else('y == np.ceil(prediction)', 'np.ceil(prediction)', -1)))\
          >> select("row", "max_col", "y", "prediction", "match")

# Manually set first and last to ensure all data is included
max_pos.at[0, "match"] = 0
max_pos.at[len(max_pos.index)-1, "match"] = len(heatmap.columns)

# Iteratively update the matches where monotonic, nearly-linear increase is detected
update = max_pos >> query('match == -1') >> count()
prev = max_pos >> count()
prev = prev.values[0][0]
while update.values[0][0] < prev :
    prev = update.values[0][0]
    max_pos = max_pos \
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

# Handle remaining blank predictions
undefined = max_pos \
            >> define(last= 'match.shift(1)', next= 'match.shift(-1)')\
            >> query("match == -1")\
            >> select("row", "max_col", "prediction", "y", "last", "next")

if len(undefined.index) > 0:
    print(undefined)
    exit("missing some assignments")

"""
# Identify sections where prediction fails
runs = [[]]
for rowNum in range(0, len(undefined.index)):
    row = int(list(undefined.iloc[rowNum].values)[0])
    if len(runs[-1]) == 0:
        runs[-1].append(row)
    elif row == runs[-1][-1] + 1:
        runs[-1].append(row)
    else:
        runs.append([row])

for run in runs:
    chunk = max_pos.iloc[run[0]-1:run[-1] + 2]
    print(calcReg(chunk))
    #new_model_x = pd.Series()
"""


#print(max_pos >> define(match=if_else('(match != -1) & ( (match.shift(1) > match) |  (match.shift(-1) < match)) ',
#                        -1, 'match')))
#for row_num in range(0,len(max_pos)):
#    max_col, max_val, pred, match, diff = max_pos.iloc[[row_num]].to_numpy()[0]
#    print(max_col, match)
#    #print(max_col, max_val, pred_low, pred_high, match)
    #for value in [pred_low, pred_high]:
    #    if max_col == value:
    #        print("match")
    #        max_pos.at[i, "match"] = value


max_pos.to_csv("tmp/max.csv")
exit()

# Evaluate predictions against actual max values
max_pos["match"], max_pos["unmatched"], groupNum = checkModel(max_pos)

#print(max_pos[~max_pos["unmatched"].isna()])
last_unmatched = max_pos["unmatched"].isna().sum()
decreasing = True


print(max_pos)
while decreasing:
    for i in max_pos.unmatched.unique():
        group = max_pos[max_pos["unmatched"] == i].copy()
        group.drop(["match", "unmatched"], inplace=True, axis=1)
        if len(group.index) > 1:
            # First, check if this is just a rounding issue where the prediction
            # line is falling slightly above/below the max line
            # To do this, use the difference of max - pred for the last on-target prediction
            # To do: make sure it can handle first/last cases
            priorRow = int(group.index.min() - 1)
            adj = max_pos["match"][priorRow] - max_pos["prediction"][priorRow]
            group["prediction"] = group["prediction"] + adj
            match, unmatch, groupNum = checkModel(group, groupNum)
            max_pos = applyChanges(match, unmatch, max_pos)

            # If it's not a simple rounding error, then recalibrate the line in this area
            if last_unmatched == max_pos["unmatched"].isna().sum():
                nextRow = int(group.index.max() + 1)
                group["prediction"] = calcReg(max_pos.iloc[priorRow:nextRow + 1, ])[1:-1]
                match, unmatch, groupNum = checkModel(group, groupNum)
                max_pos = applyChanges(match, unmatch, max_pos)
                if last_unmatched == max_pos["unmatched"].isna().sum():
                    decreasing = False

print(max_pos.dropna())
exit(0)

# Need to use standard error if the linear correction doesn't work?
print(max_pos)
    #group["meanError"] = group["prediction"] - group["max_col"]
    #nonOutliers = group[np.abs(zscore(group["meanError"]))  < 2.5]
    #print(nonOutliers["meanError"].mean())
    #elif len(group.index) == 0:
    #    continue


exit(0)

"""
    col_max = heatmap.max(axis=1)
    i, j= 0, 0
    while i < num_row and j < num_col:
        print(i,j)
        diag = heatmap.iloc[i,j]
        #row = heatmap.iloc[[i]]
        if diag == row_max[i]:
            colMatchByRow[i] = j
            # Fill in if one was just not quite the max but the rest is continuous
            if i >= 2 and colMatchByRow[i] - colMatchByRow[i - 2] == 2:
                colMatchByRow[i - 1] = j - 1
        else:
            if row_max[i] == heatmap.iloc[i,j+1]:
                j+=1
                colMatchByRow[i] = j
            else:
                colMatchByRow[i] = -1
                if i < 3 or colMatchByRow[i-1] == -1:
                    break
        i+=1
        j+=1

print(colMatchByRow)



for i in range(0,1):
    row = heatmap.iloc[[i]]
    identity = heatmap.iloc[i,i]
    print(row.max())
    #print(identity)
    exit(0)
    #if  != :
    #    print(heatmap.iloc[[i]])
    #    print("look at", i)
    #    exit(0)
by_row = dict()
for row in zscores.T.iterrows():
    rowNum, rowData = row #, colNum)
    by_row[rowNum] = rowData.idxmax()

for col in zscores.iterrows():
    colNum, colData = col  # , colNum)
    if by_row[colData.idxmax()] != colNum:
        print(colNum, colData.idxmax(), by_row[colData.idxmax()])
        print(sorted(colData))
        exit(0)


flatscores = pd.DataFrame(list(heatmap.stack()), columns=["score"])
print(flatscores)
std = flatscores.std()[0]
mean = flatscores.mean()[0]
print("mean", mean, "std", std)
hist = (
           ggplot(flatscores, aes(x='score')) +
           geom_histogram(binwidth=.05)
)
print(hist)

print((0.9698643623123117 - mean)/std)"""

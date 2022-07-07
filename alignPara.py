import pandas as pd
import numpy as np
from plotnine import *
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression

def calcReg(max_pos):
    # Draw an identity line capturing max score indices based on row number
    model = LinearRegression().fit(pd.DataFrame(max_pos.index), pd.DataFrame(max_pos["max_col"]))
    return model.predict(pd.DataFrame(max_pos.index))

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
max_pos = pd.DataFrame({'max_col': pd.to_numeric(heatmap.T.idxmax(), errors='ignore'),
                       'max_val': pd.to_numeric(heatmap.T.max(), errors='ignore')})
max_pos.index = pd.to_numeric(max_pos.index, errors='ignore')

# Predict the cells that will hold the best matches using linear regression
max_pos["prediction"] = calcReg(max_pos)

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

max_pos.to_csv("tmp/max.csv")
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

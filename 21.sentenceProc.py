from textFunctions import *
import seaborn as sns
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import spacy
from textFunctions import *
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

def heatmap(docxSentence, upstreamDocs):
    matches = list()
    for upstreamS in upstreamDocs:
        if len(upstreamS) == 0:
            matches.append(float("nan"))
        else:
            matches.append(docxSentence.similarity(upstreamS))
    return matches

def spacify(doc, nlp):
    """All of the words should be the same across the documents. However,
    symbols, whitespace and punctuation may get moved around. Drop these for comparing"""
    doc=nlp(doc)
    return nlp(" ".join([token.text for token in doc if token.pos_ not in ["SYM", "PUNCT", "SPACE"]]))

def trimTextblocks(text, skipSections):
    """Remove blocks of text from the list that are from the front matter or back matter
    Input: list of text blocks extracted from XML file
    Returns: list of text blocks expected to be found in corresponding markdown file"""
    title = ""
    body = list()
    skip = 1
    for i in range(1, len(text)):
        if re.search(r"^title:", text[i]):
            title = text[i].replace("title: ", "")
        elif re.search(r"(^#+)", text[i]):
            headerLevel = re.match(r"(#+)", text[i]).group(1)
            if len(headerLevel) == 1: # the # are front or back matter
                if len(body) > 0: # for back matter
                    break
                skip = 1
            else:
                letters = re.sub(r'[^a-zA-Z]', '', text[i])
                if letters in skipSections:
                    skip = headerLevel
                else:
                    if skip == 0 or skip == 1:
                        body.append(text[i])
                        skip = 0
                    else:
                        prior_skip = re.match(r"(#+)", skip).group(1)
                        if len(prior_skip) >= skip:
                            skip = 0
                            body.append(text[i])
        elif skip == 0:
                body.append(text[i])
    return ["# " + title] + body

# Main
"""
nlp = spacy.load('en_core_web_lg')

with open("sectionsToSkip.txt", 'r') as skipfile:
    skip = skipfile.readlines()

with open("tmp/diff.txt", 'r') as filehandle:
    diff = filehandle.readlines()
    diff = trimTextblocks(diff, skip)
    diff = [s for p in diff for s in splitSentences(p)]

with open("tmp/upstream.md", 'r') as filehandle:
    markdown = filehandle.readlines()
    upstreamParagraphs = reformatMarkdown(markdown)
    upDocx = [spacify(p, nlp) for p in upstreamParagraphs]

heatmapScores = dict()
for block_i in range(0, len(diff)):
    #if diff[block_i] == "\n":
    #    continue
    text = reconstructOrig(diff[block_i])
    blockDoc = spacify(text, nlp)
    heatmapScores[block_i] = heatmap(blockDoc, upDocx)

heatmapdf = pd.DataFrame.from_dict(heatmapScores, orient='index')
heatmapdf.to_csv("heatmap.csv", index=False)
sns.heatmap(heatmapdf)
plt.savefig('heatmap.png')
"""
# Load the scores from the heatmap
heatmap = pd.read_csv("heatmap.csv", index_col=None)


max_pos = pd.DataFrame({'max_col': pd.to_numeric(heatmap.T.idxmax(), errors='ignore'),
                        'max_val': pd.to_numeric(heatmap.T.max(), errors='ignore')})
max_pos.index = pd.to_numeric(max_pos.index, errors='ignore')
max_pos = max_pos \
          >> define(row = max_pos.index.astype("int"), diff='max_col - max_col.shift(1)')\
          >> define(z='zscore(max_val, nan_policy="omit")')\
          >> define(y=if_else('(max_val == 1)', 'max_col', 'np.nan'))\
          >> define(prediction='calcReg(row, y)')
          #>> define(match=if_else('y == np.floor(prediction)', 'np.floor(prediction)',
          #                            if_else('y == np.ceil(prediction)', 'np.ceil(prediction)', -1)))\
#>> select("row", "max_col", "max_val", "z", "y")

update = max_pos \
         >> query('max_val == 1')
#         >> count()
print(update)
max_pos.to_csv("tmp/max.csv", index=False)
#docxSentences = []
##for block in textblocks:
#    docxSentences += [reconstructOrig(text) for text in splitSentences(block)] + ['\n']





# 1.5 remove all formatting

# 2 Sentence-by-sentence mapping

# 3 using mapping, id all edits in original docx text & map to markdown

# 4 apply edits to markdown text

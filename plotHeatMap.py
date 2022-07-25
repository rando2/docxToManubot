import seaborn as sns
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import spacy
from textFunctions import *

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

def main(args):
    nlp = spacy.load('en_core_web_lg')

    with open(args.tempTextblocks, 'r') as filehandle:
        textblocks = filehandle.readlines()

    # Read in markdown pulled from upstream
    upstreamMD = readMarkdown(args.baseMarkdown)
    upstreamParagraphs = reformatMarkdown(upstreamMD)
    upDocx =[spacify(p, nlp) for p in upstreamParagraphs]

    heatmapScores = dict()
    for block_i in range(0, len(textblocks)):
        if textblocks[block_i] == "\n":
            continue
        text = reconstructOrig(textblocks[block_i])
        blockDoc = spacify(text, nlp)
        heatmapScores[block_i] = heatmap(blockDoc, upDocx)

    heatmapdf = pd.DataFrame.from_dict(heatmapScores, orient='index')
    heatmapdf.to_csv("heatmap.csv", index=False)

    sns.heatmap(heatmapdf)
    plt.savefig('heatmap.png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseMarkdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    parser.add_argument('tempTextblocks',
                        help='temp text file to store textblocks pulled from diff',
                        type=str)
    parser.add_argument('tempIndices',
                        help='temp text file to store indices of changes pulled from diff',
                        type=str)
    parser.add_argument('matchedPara',
                        help='temp text file to store corresponding docx and upstream text',
                        type=str)
    args = parser.parse_args()
    main(args)

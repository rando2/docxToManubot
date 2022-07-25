import ast
from textFunctions import *
from statsFunctions import *
import argparse
import spacy
import pandas as pd
import numpy as np
import seaborn as sns

def reconstructOrig(text):
    # Find references and track changes metadata
    annotations = re.compile(r" \{\+.*?\+\}| \\\[\[[0-9]+[^A-Za-z]*\\\]")
    text = re.sub(annotations, "", text)
    # Can have some stray metadata because of linebreaks
    text = re.sub("\[.*?\]\{.*\}", "", text)
    # Remove the annotations around deletions
    text = re.sub("-\]|\[-", "", text)
    return text

def reformatMarkdown(markdown):
    paragraphs = list()
    currentPara = []
    for line in markdown:
        # Remove markdown comments that won't appear in docx
        line = re.sub("<!--.*?-->+", "", line)
        currentPara.append(line)
        # look for lines that are only whitespace
        if not re.search(r"\S", line):
            paragraphs.append(" ".join(currentPara))
            currentPara = []
    return paragraphs

def heatmap(docxSentence, upstreamDocs):
    matches = list()
    for upstreamS in upstreamDocs:
        if len(upstreamS) == 0:
            matches.append(float("nan"))
        else:
            matches.append(docxSentence.similarity(upstreamS))
    return matches

def findOriginal(docxSentence, upstreamDocs, startMD =0, runData = None):
    matches = list()
    print(docxSentence)
    for upstreamS in upstreamDocs:
        if len(upstreamS) == 0:
            matches.append(float("nan"))
        else:
            matches.append(docxSentence.similarity(upstreamS))
    return matches
    maxScore = np.nanmax(matches)
    if runData is None:
        runData = initStats(matches)
    else:
        runData = updateStats(runData, maxScore)
    z = retrieveZ(runData, maxScore)
    if matches.index(maxScore) < startMD:
        print([m for m in matches if m > 0.9])
        # calc standard deviation?
        print(maxScore, z)
        print(upstreamS)
    return  + matches.index(maxScore), runData

def main(args):
    nlp = spacy.load('en_core_web_lg')

    # Read in markdown pulled from upstream
    upstreamMD = readMarkdown(args.baseMarkdown)
    upstreamParagraphs = reformatMarkdown(upstreamMD)
    upstreamDocs = [nlp(sentence) for sentence in upstreamMD]

    # Read in textblocks and indices of changes as identified in two previous steps
    with open(args.tempTextblocks, 'r') as filehandle:
        textblocks = filehandle.readlines()

    docxindex = 0
    heatmapScores = dict()
    for block in textblocks:
        text = " ".join(block)
        text = reconstructOrig(text)
        text = splitSentences(text)

        for i in range(0, len(text)):
            docxSentenceDoc = nlp(text[i])
            heatmapScores[docxindex] = heatmap(docxSentenceDoc, upstreamDocs)
            docxindex += 1
    heatmapdf = pd.DataFrame.from_dict(heatmapScores, orient='index')
    heatmapdf.to_csv("heatmap.csv")
    print(sns.heatmap(heatmapdf, annot=True))

    #with open(args.tempIndices, 'r') as filehandle:
    #    textToEval = [block.rstrip() for block in filehandle.readlines()]
    """
    # Examining each paragraph that contains edits
    companionParas = list()
    startMD = 0
    runData = None
    previous = 0
    for indexNum in range(0, len(textToEval)):
        # Evaluate the list of lists of indices & retrieve the corresponding blocks of text
        start, stop = [int(i) for i in ast.literal_eval(textToEval[indexNum])]

        # If the last block lacked enough text to match, then adjust the span here
        if previous == 1:
            start = int(ast.literal_eval(textToEval[indexNum-1])[0])

        # Pull text in the range of the indices
        text = " ".join(textblocks[start:stop])
        text = reconstructOrig(text)
        text = splitSentences(text)

        addText = ""
        heatmapScores = dict()
        for i in range(0, len(text)):
            docxSentenceDoc = nlp(text[i])
            heatmapScores[i] = heatmap(docxSentenceDoc, upstreamDocs)
            #testSentence = addText + docxSentence
            #if len(re.findall("(\w+)", testSentence)) >= 5:
            #    if startMD == 0:
            #        startMD, runData = findOriginal(nlp(testSentence), upstreamDocs)
            #    else:
            #        startMD, runData = findOriginal(nlp(testSentence), upstreamDocs, startMD, runData)
            #    companionParas.append([testSentence, upstreamMD[startMD]])
            #    addText = ""
            #else:
            #    addText = testSentence
        heatmapdf = pd.DataFrame.from_dict(heatmapScores, orient='index')
        heatmapdf.to_csv("heatmap.csv")
        sns.heatmap(heatmapdf, annot=True)
    # Write to temporary file
    #with open(args.matchedPara, 'w') as filehandle:
    #    filehandle.writelines("%s\n" % i for i in companionParas)



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

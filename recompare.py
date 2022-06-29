import ast
from textFunctions import *
from statsFunctions import *
import argparse
from fuzzywuzzy import fuzz
import spacy

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
        currentPara.append(line)
        # look for lines that are only whitespace
        if not re.search(r"\S", line):
            paragraphs.append(" ".join(currentPara))
            currentPara = []
    return paragraphs

def findOriginal(editedDoc, upstreamDocs, lastParaNum = 0, runData = None):
    matches = list()
    if runData is None:
        for p in upstreamDocs:
            matches.append(editedDoc.similarity(p))
        print(matches)
        return matches.index(max(matches)), initStats(matches)
    else:
        for paraI in range(lastParaNum+1 ,len(upstreamDocs)):
            match = editedDoc.similarity(upstreamDocs[paraI])
            runData = updateStats(runData, match)
            matches.append(match)
            z = retrieveZ(runData, match)
            print(match, z)
            if z >= 2:
                return paraI, runData
        maxScore = max(matches)
        z = retrieveZ(runData, maxScore)
        return lastParaNum + matches.index(max(matches)), runData

def main(args):
    nlp = spacy.load('en_core_web_lg')

    # Read in markdown pulled from upstream
    upstreamMD = readMarkdown(args.baseMarkdown)
    upstreamParagraphs = reformatMarkdown(upstreamMD)
    upstreamDocs = [nlp(p) for p in upstreamParagraphs]

    # Read in textblocks and indices of changes as identified in two previous steps
    with open(args.tempTextblocks, 'r') as filehandle:
        textblocks = filehandle.readlines()
    with open(args.tempIndices, 'r') as filehandle:
        textToEval = [block.rstrip() for block in filehandle.readlines()]

    # Examining each paragraph that contains edits
    companionParas = list()
    startPara = 0
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

        # If inserting paragraph breaks, can end up with short paragraphs
        # Better to do this as regex for non-white space most likely
        # 5 words is just a guess for a good number to achieve a unique match
        if len(re.findall("(\w+)", text)) < 5:
            previous = 1
            continue
        else:
            previous = 0

        # Pull the corresponding paragraph from markdown
        if startPara == 0:
            startPara, runData = findOriginal(nlp(text), upstreamDocs)
        else:
            startPara, runData = findOriginal(nlp(text), upstreamDocs, startPara, runData)
        print(text)
        companionParas.append([nlp(text), upstreamParagraphs[startPara]])

    # Write to temporary file
    with open(args.matchedPara, 'w') as filehandle:
        filehandle.writelines("%s\n" % i for i in companionParas)
#change = re.compile("(\[-.+?-\]*) (\{\+.*?\+\})")
#for (square, curly) in re.findall(change, text):


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

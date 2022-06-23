from textFunctions import *
import argparse
from fuzzywuzzy import fuzz
import re
import ast

def sentenceBySentence(originalSentences, markdownParaList):
    """Compare each sentence to identify the better hit. This will ensure that
    spurious hits (e.g., caused by whitespace) are removed"""
    bestMatch = [0, 0]
    numSentences = len(originalSentences)
    for candidate in markdownParaList:
        matches = list()
        for s in range(0, numSentences):
            docxSentence = originalSentences[s]
            markdownSentence = candidate[s]
            matchScore = fuzz.partial_ratio(docxSentence, markdownSentence)
            matches.append(matchScore)
        if sum(matches) > bestMatch[0]:
            bestMatch = [sum(matches), candidate]
    return(bestMatch[1])

def findBestHit(originalSentences, markdown, mdi):
    numSentences = len(originalSentences)
    maxScore = 0
    bestHits = list()
    originalPara = " ".join(originalSentences)
    while mdi < (len(markdown) - numSentences):
        markdownPara = " ".join(markdown[mdi:mdi+numSentences])
        matchScore = fuzz.partial_ratio(originalPara, markdownPara)
        if matchScore > maxScore:
            maxScore = matchScore
            bestHits = [markdownPara]
        elif matchScore == maxScore:
            bestHits.append(markdownPara)
        elif maxScore >= 95 and matchScore < maxScore:
            # speed things up by accepting the first very strong match(es)
            break
        mdi +=1
    return bestHits, mdi

def genRawText(edTextBlocks):
    # Use the annotation to assign blocks to reconstruct the original (unchanged + deleted) and edited
    # (unchanged + inserted) text
    original_text = str()
    edited_text = str()
    for blockIndex in range(0,len(edTextBlocks)):
        docxText = edTextBlocks[blockIndex]
        if docxText[:3] == "~~~":
            # Text that was deleted will be in the original but not the edits
            original_text += cleanAnnotations(docxText)
        elif docxText[:3] == "***": # Text that was deleted will be in the original but not the edits
            edited_text += cleanAnnotations(docxText)
        else:
            original_text += docxText
            edited_text += docxText

def genOrigSentences(blocks, start, stop):
    # Create sentences from blocks of text extracted from docx
    originalText = "".join([text for text in blocks[start:stop] if
                            (text[0:3] != "***" and not
                            bool(re.search('([0-9]\.[0-9])', text)))])
    print(originalText)
    return splitSentences(originalText.replace("~~~", ""))

def checkBestHit(bestHits, originalSentences):
    if len(bestHits) == 1:
        return bestHits[0]
    elif len(bestHits) > 1:
        bestHit = sentenceBySentence(originalSentences, bestHits)
        return bestHit
    else:
        return None

def matchSentences(textblocks, start, stop, markdown, mdi):
    """Compare this block of edits against the markdown file upstream
    Start at the last match to cut down on search space"""
    originalSentences = genOrigSentences(textblocks, start, stop)

    bestHits, mdi = findBestHit(originalSentences, markdown, mdi)
    bestHit = checkBestHit(bestHits, originalSentences)
    if bestHit is not None:
        return bestHit, mdi
    else:# if this isn't anchored, we'll need to search on the *edited* text for replacing
        originalSentences = genOrigSentences(textblocks, findLastNormal(textblocks, start), stop)
        bestHits, mdi = findBestHit(originalSentences, markdown, mdi)
        bestHit = checkBestHit(bestHits, originalSentences)
        if bestHit is not None:
            return bestHit, mdi
        else:
            print("No match found for")
            print(originalSentences)
            exit("matchSentences")

def fuzzFriendlyMD(markdown):
    edMD = "\n".join(markdown)
    return splitSentences(edMD)

def main(args):
    # Read in the markdown pulled from upstream. Then, split the sentences using the same
    # algorithm used to define sentences in the docx text so that the formatting will be
    # the same across documents. When we actually replace text in markdown, we won't do this
    # pre-processing step -- it's just for finding a match across documents
    markdown = fuzzFriendlyMD(readMarkdown(args.baseMarkdown))

    # Read in list of lists indicating the ranges of indices that correspond to edits
    # from 01. and 02.
    with open('docx-to-manubot-tmp/textblocks.txt', 'r') as filehandle:
        textblocks = filehandle.readlines()
    with open('docx-to-manubot-tmp/textIndices.txt', 'r') as filehandle:
        textToEval = [block.rstrip() for block in filehandle.readlines()]

    # Evaluate each edit and replace in markdown
    mdPos = 0
    hits = list()
    for editIndices in textToEval:
        #print(editIndices)
        # Evaluate the list of lists and retrieve the corresponding blocks of text
        start, stop = [int(i) for i in ast.literal_eval(editIndices)]

        # Locate each text block from docx in the markdown file
        # using [lastUneditedBlock, nextUneditedBlock) to avoid overlap
        hit, mdPos = matchSentences(textblocks, start, stop + 1, markdown, mdPos)
        hits.append([start, stop, mdPos])
    writeList(hits, "matchIndices.txt")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseMarkdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    args = parser.parse_args()
    main(args)

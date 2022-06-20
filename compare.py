from textFunctions import *
import argparse
from fuzzywuzzy import fuzz
import re
import ast

def sentenceBySentence(originalSentences, markdown, candidateIndex):
    """Compare each sentence to identify the better hit. This will ensure that
    spurious hits (e.g., caused by whitespace) are removed"""
    bestMatch = [0, 0]
    numSentences = len(originalSentences)
    for i in candidateIndex:
        matches = list()
        for s in range(0, numSentences):
            docxSentence = originalSentences[s]
            markdownSentence = markdown[i+s]
            matchScore = fuzz.partial_ratio(docxSentence, markdownSentence)
            matches.append(matchScore)
        if sum(matches) > bestMatch[0]:
            bestMatch = [sum(matches), i]
    return(bestMatch[1])

def findBestHit(originalSentences, markdown):
    numSentences = len(originalSentences)
    mdi = 0 # markdown index
    maxScore = 0
    bestHits = list()
    while mdi < (len(markdown) - numSentences):
        markdownSentences = markdown[mdi:mdi+numSentences]
        matchScore = fuzz.partial_ratio(originalSentences, markdownSentences)
        if matchScore > maxScore:
            maxScore = matchScore
            bestHits= [mdi]
        elif matchScore == maxScore:
            bestHits.append(mdi)
        mdi +=1
    return bestHits

def matchSentences(textblocks, start, stop, markdown):
    """Compare this block of edits against the markdown file upstream"""
    # Create sentences from blocks of text extracted from docx
    textToEdit = textblocks[start:stop]

    originalText = "".join([text for text in textToEdit if (text[0:3] != "***" and not
    bool(re.search('([0-9]\.[0-9])', text)))])
    originalSentences = splitSentences(originalText.replace("~~~", ""))

    bestHits = findBestHit(originalSentences, markdown)
    if len(bestHits) == 1:
        return bestHits[0]
    elif len(bestHits) == 0:
        print("No match found for")
        print(originalSentences)
        new_start = start -1
        #while new_start >= 0:
        #    if
        exit()
    else:
        return sentenceBySentence(originalSentences, markdown, bestHits)

def modifyText(textblocks, markdown, mdi):
    """Want to replace the minimum number of characters possible to avoid issues
    with references, manubot & HTML formatting, etc."""
    numSentences = len(splitSentences("".join(textblocks)))
    try:
        markdown_text = " ".join(markdown[mdi:mdi+numSentences])
    except TypeError:
        print(mdi, type(mdi), numSentences, type(numSentences))
        exit(1)
    # Use the annotation to assign blocks to reconstruct the original (unchanged + deleted) and edited
    # (unchanged + inserted) text
    original_text = str()
    edited_text = str()
    for blockIndex in range(0,len(textblocks)):
        docxText = textblocks[blockIndex]
        if docxText[:3] == "~~~":
            # Text that was deleted will be in the original but not the edits
            original_text += cleanAnnotations(docxText)
        elif docxText[:3] == "***": # Text that was deleted will be in the original but not the edits
            edited_text += cleanAnnotations(docxText)
        else:
            original_text += docxText
            edited_text += docxText

    # Ensure these are paragraphs with spaces between sentences (can be lost due to trimming)
    # and clean up the annotations (~~~ and ***)
    original_text = " ".join(splitSentences(original_text))
    original_text = cleanAnnotations(original_text)

    edited_text = " ".join(splitSentences(edited_text))
    edited_text = cleanAnnotations(edited_text)

    markdown_text = markdown_text.replace(original_text, edited_text)
    markdown = markdown[:mdi] + \
                      cleanMarkdown(markdown_text) + \
                      markdown[mdi+len(original_text):]
    return markdown

def main(args):
    # Read in the markdown pulled from upstream
    markdown = readMarkdown(args.baseMarkdown)

    # Read in list of lists indicating the ranges of indices that correspond to edits
    # from 01. and 02.
    with open('docx-to-manubot-tmp/textblocks.txt', 'r') as filehandle:
        textblocks = filehandle.readlines()
    with open('docx-to-manubot-tmp/textIndices.txt', 'r') as filehandle:
        textToEval = [block.rstrip() for block in filehandle.readlines()]

    # Evaluate each edit and replace in markdown
    for editIndices in textToEval:
        print(editIndices)
        # Evaluate the list of lists and retrieve the corresponding blocks of text
        start, stop = [int(i) for i in ast.literal_eval(editIndices)]

        # Locate each text block from docx in the markdown file
        # using [lastUneditedBlock, nextUneditedBlock) to avoid overlap
        mdPos = matchSentences(textblocks, start, stop, markdown)

        # Replace the lines of the upstream markdown that match the sentences
        # derived from the edits in the docx file
        markdown = modifyText(textToEdit, markdown, mdPos)

    print("Writing", args.mdOutput)
    writeMarkdown(markdown, args.mdOutput)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseMarkdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    parser.add_argument('mdOutput',
                        help='Path of the md file where the edited markdown text will be stored',
                        type=str)
    args = parser.parse_args()
    main(args)

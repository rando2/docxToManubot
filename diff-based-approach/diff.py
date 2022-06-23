from textFunctions import *
import argparse
import re
import ast
from fuzzywuzzy import fuzz

def findBestHit(line, markdown):
    mdi = 0 # markdown index
    maxScore = 0
    bestHit = list()
    while mdi < len(markdown):
        matchScore = fuzz.partial_ratio(line, markdown[mdi])
        if matchScore > maxScore:
            maxScore = matchScore
            bestHit = [mdi]
        elif matchScore == maxScore:
            bestHit.append(mdi)
        elif maxScore >= 98 and matchScore < maxScore:
            # speed things up by accepting the first very strong match(es)
            break
        mdi +=1

    if len(bestHit) > 1:
        print("problem: multiple anchors")
        print(repr(line))
        exit(1)
    return bestHit[0]

def replaceText(replacements, markdown):
    markdown_index = 0
    for edit in replacements:
        basePos, lines = edit

        # Try reformating the text, removing the diff markup and cleaning up the sentences
        changes = [line[0] for line in lines]
        sentences = [l[2:] for l in lines]

        # Pull the index of the corresponding text in the upstream markdown file
        anchor = None # will throw error if this isn't found before we start analyzing changes
        for i in range(0, len(changes)):
            if anchor is None:
                anchor = findBestHit(sentences[i], markdown[markdown_index:])

            if changes[i] == "+":
                markdown = markdown[:anchor + i] + [sentences[i]] + markdown[anchor + i:]
            elif changes[i] == "-":
                markdown = markdown[:anchor + i] + markdown[anchor + i + 1:]
            elif changes[i] == "!":
                edit_fragments = re.split(r"\\\[\S+\]", sentences[i])
                print(edit_fragments)

def resetVariables():
    return tuple(), list()

def parseDiffSyntax(lines):
    replacements = list()
    section = ""
    basePos, new_text = resetVariables()
    for line in lines:
        if line[0] == "*":  # new block or baseline position
            section = "base"
            try: # positions in baseline file
                basePos = ast.literal_eval(re.search(r"\*+ ([0-9]+,*[0-9]*)", line).group(1))
            except AttributeError:  # if it's a new diff block, reset
                # adjust for 1-indexing
                replacements.append([basePos, new_text])
                basePos, new_text = resetVariables()
        elif bool(re.search(r"-+ [0-9]+,*[0-9]*", line)):
            section = "edited"
        else: # if it's text
            if section == "edited":
                new_text.append(line)
    return replacements

def main(args):
    origMarkdown = readMarkdown(args.baseFile)

    with open(args.diffFile, 'r') as diffFile:
        diff = diffFile.read()
        diff = diff.splitlines()
    replacements = parseDiffSyntax(diff[3:])
    replaceText(replacements, origMarkdown)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseFile',
                        help='Path of the md file to be cleaned',
                        type=str)
    parser.add_argument('diffFile',
                        help='Path of the file produced by diffing the edited file against the base',
                        type=str)
    args = parser.parse_args()
    main(args)

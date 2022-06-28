import re
import argparse
from textFunctions import *

def readSectionNames(fname):
    with open(fname, "r") as fin:
        return fin.read().splitlines()

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

def main(args):
    # Identify which text has stayed the same and which has changed
    with open(args.tempDiff, 'r') as diffFile:
        text = diffFile.readlines()
    text = trimTextblocks(text, readSectionNames(args.sectionsToSkip))
    with open(args.tempTextblocks, 'w') as filehandle:
        filehandle.writelines("%s" % i for i in text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('sectionsToSkip',
                        help='TXT file with names of sections that should not be analyzed, one per line',
                        type=str)
    parser.add_argument('tempDiff',
                        help='TXT file with the diff of the document without & with track changes',
                        type=str)
    parser.add_argument('tempTextblocks',
                        help='temp text file to store textblocks pulled from diff',
                        type=str)
    args = parser.parse_args()
    main(args)

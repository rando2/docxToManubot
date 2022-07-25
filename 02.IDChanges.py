from textFunctions import *
import re
import argparse

def selectBlocksToSearch(textblocks):
    """Use the mark-up in the textblocks list to create blocks of unedited text surrounding edited text
    input: list of blocks of text
    output: list of indices for last and next unchanged blocks for each edit"""

    blocksToEvaluate = list() # list of lists to be returned
    lastNormal = int() # track indices of normal blocks
    i=0
    while i < len(textblocks):
        if not re.search(r"\[-|-\]|\{\+|\+\}", textblocks[i]):
            lastNormal = i
        else: # for modified blocks
            blockRange = [0, 0]
            if lastNormal >= 0:
                blockRange[0] = lastNormal # last normal block, or default of 0 (beginning)

            nextNormal = findNextNormal(textblocks, i)
            if nextNormal < 0: # will return negative if normal not found
                blockRange[1] = len(textblocks)
            else:
                blockRange[1] = nextNormal
                lastNormal = nextNormal
            # Don't need to re-evaluate any blocks incorporated into this one
            blocksToEvaluate.append(blockRange)
            i = blockRange[1]
        i += 1
    return blocksToEvaluate

def main(args):
    # Read in the textblocks parsed from XML in previous step
    with open(args.tempTextblocks, 'r') as filehandle:
        textblocks = filehandle.readlines()

    # Identify the range of indices that correspond to edits
    textIndices = selectBlocksToSearch(textblocks)
    with open(args.tempIndices, 'w') as filehandle:
        filehandle.writelines("%s\n" % i for i in textIndices)

    # Extract a list of contributors & compare to input file listing word x github identifiers

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('tempTextblocks',
                        help='temp text file to store textblocks pulled from diff',
                        type=str)
    parser.add_argument('tempIndices',
                        help='temp text file to store indices of changes pulled from diff',
                        type=str)
    args = parser.parse_args()
    main(args)

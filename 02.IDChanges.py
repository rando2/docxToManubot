from textFunctions import *

def selectBlocksToSearch(textblocks):
    """Use the mark-up in the textblocks list to create blocks of unedited text surrounding edited text
    input: list of blocks of text
    output: list of indices for last and next unchanged blocks for each edit"""

    blocksToEvaluate = list() # list of lists to be returned
    lastNormal = int() # track indices of normal blocks
    i=0
    while i < len(textblocks):
        if textblocks[i][:3] not in ["~~~", "***"]:
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

def main():
    # Read in the textblocks parsed from XML in previous step
    with open('docx-to-manubot-tmp/textblocks.txt', 'r') as filehandle:
        textblocks = filehandle.readlines()

    # Identify the range of indices that correspond to edits
    textIndices = selectBlocksToSearch(textblocks)
    writeList(textIndices, "textIndices.txt")

if __name__ == '__main__':
    main()

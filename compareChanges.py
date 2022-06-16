from fuzzywuzzy import fuzz
import argparse
import re
import pysbd

def retrieveDocx():
    textblocks = []
    with open('listfile.txt', 'r') as filehandle:
        textblocks = [block.rstrip() for block in filehandle.readlines()]

def findNextNormal(textblocks, i):
    """Increment forward until find the next normal block"""
    while i < len(textblocks):
        if textblocks[i][:3] not in ["~~~", "***"]:
            return i
        i += 1
    return -1

def cleanAnnotations(text):
    text = text.replace("~~~", "")
    text = text.replace("***", "")
    return text

def splitSentences(text):
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def readMarkdown(mdfile):
    with open(mdfile, 'r') as origFile:
        # Read & format original markdown
        origTextRaw = origFile.read()
        origText = origTextRaw.splitlines()
        origText = [t.strip() for t in origText]
        return origText

def groupTextBlocks(textblocks):
    """Use the mark-up in the textblocks list to create a python-readable track changes document"""
    edited = [i for i in range(len(textblocks)) if textblocks[i][:3] in ["~~~", "***"]]
    editedIndex = 0
    while editedIndex < len(edited) - 1:
        if editedIndex == 0: # for first edit, normal text until 2nd edit
            markdown = locateText(textblocks[:edited[editedIndex+1]], markdown)
        elif editedIndex == len(edited)-1: # for the last edit, normal text since 2-to-last edit
            markdown = locateText(textblocks[edited[editedIndex-1]:], markdown)
        else:
            # if there is a normal block before next edit
            if edited[editedIndex+1] - edited[editedIndex] > 1:
                markdown = locateText(textblocks[edited[editedIndex-1]+1:edited[editedIndex+1]], markdown)
            else: # if multiple edits in a row
                startEditing = editedIndex
                while editedIndex < len(edited) - 1 and \
                        edited[editedIndex+1] - edited[editedIndex] == 1: #increment until hit gap
                    editedIndex +=1
                if len(edited) - editedIndex <= 1: # if it's the last edit
                    markdown = locateText(textblocks[edited[startEditing - 1] + 1:], markdown)
                else:
                    markdown = locateText(textblocks[edited[startEditing - 1] + 1:edited[editedIndex+1]],
                                          markdown)
        editedIndex += 1
    return markdown

def locateText(textblocks, markdown):
    """Locate the corresponding text to this section of the docx in the markdown file by
     comparing the first and last sentences to the markdown file to find the closest match.
    Save the indices of the best matches in the list of sentences from the markdown file
    (the textblock should correspond to a continuous block of text in the markdown file)"""

    markdown_bounds = [0, 0]
    if len(originalSentences) == 1:
        markdown_bounds[0] = matchSentence(originalSentences[0], markdown)
        markdown_bounds[1] = markdown_bounds[0] + 1
    else:
        try:
            for i in range(-1, 1):  # first and last, aka -1 and 0
                markdown_bounds[i] = matchSentence(originalSentences[i], markdown)
        except IndexError:
            print(originalText)
    return modifyText(textblocks, markdown, markdown_bounds)

def matchSentence(docxSentence, markdown):
    bestMatch = [0, 0]
    for mdi in range(0, len(markdown)):
        markdownSentence = markdown[mdi]
        matchScore = fuzz.partial_ratio(docxSentence, markdownSentence)
        if matchScore > bestMatch[0]:
            bestMatch = [matchScore, mdi]
    return bestMatch[1]

    # Create a list of sentences from the textblocks, skipping the section numbers and
    # any insertions (since insertions won't match to the old text)
    originalText = "".join([text for text in textblocks if (text[0:3] != "***" and not
                                                            bool(re.search('([0-9]\.[0-9])', text)))])
    originalSentences = splitSentences(originalText.replace("~~~",""))
    return originalSentences

def modifyText(textblocks, markdown, mdi):
    """Want to replace the minimum number of characters possible to avoid issues
    with references, manubot & HTML formatting, etc."""
    markdown_text = " ".join(markdown[mdi[0]: mdi[1]+1])
    normal = list()
    replacements = dict()
    for blockIndex in range(0,len(textblocks)):
        if textblocks[blockIndex][:3] not in ["~~~", "***"]:
            # Skip text that was not edited
            normal = normal.append(blockIndex)
            continue
        elif len(normal) > 0: # If there is unedited text before these edits
            if textblocks[blockIndex][:3] == "~~~":
                # For deletions, original text is the leading text + deleted content
                original_text = "".join(textblocks[normal[-1]:blockIndex + 1])
            elif textblocks[blockIndex][:3] == "***":
                # For insertions, original text is just leading text
                original_text = textblocks[blockIndex - 1]
            edited_text = "".join(textblocks[blockIndex - 1:blockIndex + 1])
        elif blockIndex < len(textblocks):
            # work forwards to find last unedited block and textblocks[blockIndex + 1][:3] not in ["~~~", "***"]:
            # If there is unedited text after
            if textblocks[blockIndex][:3] == "~~~":
                original_text = "".join(textblocks[blockIndex:blockIndex + 2])
            elif textblocks[blockIndex][:3] == "***":
                original_text = textblocks[blockIndex+1]
            edited_text = "".join(textblocks[blockIndex:blockIndex + 2])
        else:
            print("need to handle case of unanchored edits")
            print(textblocks[blockIndex])
        replacements[original_text] = edited_text

    for original_text, edited_text in replacements.items():
        # Clean up and make replacement
        original_text = cleanAnnotations(original_text)
        edited_text = cleanAnnotations(edited_text)
        markdown_text = markdown_text.replace(original_text, edited_text)

    markdown[mdi[0]:mdi[1]+1] = cleanMarkdown(markdown_text)
    return markdown

def main(args):
    # Read in the textblocks parsed from XML in previous step
    docxSentences = retrieveDocx()

    # Read in the markdown pulled from upstream
    markdown = readMarkdown(args.baseMarkdown)

    # Read in the blocks of text

    # Locate each text block from docx in the markdown file and replace
    #edited_markdown = groupTextBlocks(text, markdown)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseMarkdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    args = parser.parse_args()
    main(args)



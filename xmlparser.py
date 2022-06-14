import xml.etree.ElementTree as ET
import pysbd
import re
from fuzzywuzzy import fuzz

def readMarkdown(mdfile):
    with open(mdfile, 'r') as origFile:
        # Read & format original markdown
        origTextRaw = origFile.read()
        origText = origTextRaw.splitlines()
        origText = [t.strip() for t in origText]
        return origText

def findChanges(xmlFile):
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    # Iterate through body, storing original text as it is encountered
    # Each block of text as rendered in the XML file is stored as an item in a list
    # Insertions are marked with *** and deletions are marked with ~~~
    # This essentially renders the docx text into Python-readable track changes
    textblocks = []
    for para in root[0].findall('.//w:p', nsmap): #each paragraph
        for section in para:
            if len(section.attrib) == 0:
                for textBlock in section.findall('.//w:t', nsmap):
                    textblocks.append(textBlock.text)
            else: # these are the insertions + some random metadata changes
                for data in section.findall('.//w:r//w:t', nsmap):
                    insertedText = data.text
                    textblocks.append("***"+insertedText+"***")
                for data in section.findall('.//w:r//w:delText', nsmap):
                    deletedText = data.text
                    textblocks.append("~~~"+deletedText+"~~~")
    return textblocks

def cleanAnnotations(text):
    text = text.replace("~~~", "")
    text = text.replace("***", "")
    return text

def modifyText(textblocks, markdown, mdi):
    """Want to replace the minimum number of characters possible to avoid issues
    with references, manubot & HTML formatting, etc."""
    markdown_text = " ".join(markdown[mdi[0]: mdi[1]+1])
    print("new block")
    print(markdown_text)
    for blockIndex in range(0,len(textblocks)):
        edited_text = ""
        original_text = ""
        if blockIndex > 0 and textblocks[blockIndex - 1][:3] not in ["~~~", "***"]:
            # If there is unedited text before (a preface)
            if textblocks[blockIndex][:3] == "~~~":
                # For deletions, original text is preface + deleted content
                original_text = "".join(textblocks[blockIndex - 1:blockIndex + 1])
            elif textblocks[blockIndex][:3] == "***":
                # For insertions, original text is just preface
                original_text = textblocks[blockIndex - 1]
            edited_text = "".join(textblocks[blockIndex - 1:blockIndex + 1])
        elif blockIndex < len(textblocks) and textblocks[blockIndex + 1][:3] not in ["~~~", "***"]:
            # If there is unedited text after
            if textblocks[blockIndex][:3] == "~~~":
                original_text = "".join(textblocks[blockIndex:blockIndex + 2])
            elif textblocks[blockIndex][:3] == "***":
                original_text = textblocks[blockIndex+1]
            edited_text = "".join(textblocks[blockIndex:blockIndex + 2])
        else:
            print("need to handle case of unanchored edits")

        # Clean up and make replacement
        edited_text = cleanAnnotations(edited_text)
        original_text = cleanAnnotations(original_text)
        markdown_text = markdown_text.replace(original_text, edited_text)
    print(markdown_text)
    markdown[mdi[0]:mdi[1]+1] = cleanMarkdown(markdown_text)
    return markdown

def cleanMarkdown(text):
    text = text.replace(" #", "\n\n#")
    text = text.replace("  ", "\n")
    return splitSentences(text)

def splitSentences(text):
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def locateText(textblocks, markdown):
    """Locate the corresponding text to this section of the docx in the markdown file"""

    # Create a list of sentences from the textblocks, skipping the section numbers and
    # any insertions (since insertions won't match to the old text)
    originalText = "".join([text for text in textblocks if (text[0:3] != "***" and not
                                                            bool(re.search('([0-9]\.[0-9])', text)))])
    originalSentences = splitSentences(originalText.replace("~~~",""))

    # Compare the first and last sentences to the markdown file to find the closest match.
    # Save the indices of the best matches in the list of sentences from the markdown file
    # (the textblock should correspond to a continuous block of text in the markdown file)
    markdown_bounds = [0, 0]
    for i in range(-1,1): #first and last, aka -1 and 0
        docxSentence = originalSentences[i]
        bestMatch = [0, 0]
        for mdi in range(0,len(markdown)):
            markdownSentence = markdown[mdi]
            matchScore = fuzz.partial_ratio(docxSentence, markdownSentence)
            if matchScore > bestMatch[0]:
                bestMatch = [matchScore, mdi]
        markdown_bounds[i] = bestMatch[1]
    modifyText(textblocks, markdown, markdown_bounds)

def groupBlocks(textblocks, markdown):
    """Use the mark-up in the textblocks list to determine whether we are deleting, inserting
    or replacing text. To do this, pull the most recent normal block"""
    edited = [i for i in range(len(textblocks)) if textblocks[i][:3] in ["~~~", "***"]]
    editedIndex = 0
    while editedIndex < len(edited) - 1:
        print("index is:", editedIndex, textblocks[edited[editedIndex]])
        if editedIndex == 0: # for first edit, normal text until 2nd edit
            locateText(textblocks[:edited[editedIndex+1]], markdown)
        elif editedIndex == len(edited)-1: # for the last edit, normal text since 2-to-last edit
            locateText(textblocks[edited[editedIndex-1]:], markdown)
        else:
            # if there is a normal block before next edit
            if edited[editedIndex+1] - edited[editedIndex] > 1:
                locateText(textblocks[edited[editedIndex-1]+1:edited[editedIndex+1]], markdown)
            else: # if multiple edits in a row
                startEditing = editedIndex
                while editedIndex < len(edited) - 1 and \
                        edited[editedIndex+1] - edited[editedIndex] == 1: #increment until hit gap
                    editedIndex +=1
                if len(edited) - editedIndex <= 1: # if it's the last edit
                    locateText(textblocks[edited[startEditing - 1] + 1:], markdown)
                else:
                    locateText(textblocks[edited[startEditing - 1] + 1:edited[editedIndex+1]],
                               markdown)
        editedIndex += 1

    # insertion on its own
    # insertion next to a deletion

def main():
    # Pull the markdown from master
    markdown = readMarkdown('markdown_example.md')

    # Identify which text has stayed the same and which has changed
    text = findChanges("./word/document.xml")
    groupBlocks(text, markdown)
    print(markdown)

main()

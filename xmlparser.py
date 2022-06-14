import xml.etree.ElementTree as ET
import pysbd
import re
from fuzzywuzzy import fuzz

def readMarkdown():
    with open("origmdMD.md", 'r') as origFile:
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

def modifyText(textblocks, markdown, mdi):



    # if n == 0

def splitSentences(text):
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def locateText(textblocks, markdown):
    #print("here's what to edit", textblocks)
    insertions = sum([i[0:3] == "***" for i in textblocks])
    deletions = sum([i[0:3] == "~~~" for i in textblocks])
    print(insertions, deletions)

    originalText = "".join([text for text in textblocks if (text[0:3] != "***" and not
                                                            bool(re.search('([0-9]\.[0-9])', text)))])
    originalText = originalText.replace("~~~","")
    originalSentences = splitSentences(originalText)
    for docxSentence in originalSentences:
        bestMatch = [0, ""]
        for markdownSentence in markdown:
            matchScore = fuzz.partial_ratio(docxSentence, markdownSentence)
            if matchScore > bestMatch[0]:
                bestMatch = [matchScore, markdownSentence]
        print(docxSentence, bestMatch)
        print(textblocks)


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
        break






        continue
        if textblocks[i][:3] == "~~~":
            if textblocks[i+1][:3] == "***":
                print("replace", i, normal[n_index], textblocks[i:i+2])
            else:
                print("delete", i, normal[n_index], textblocks[i])
        elif textblocks[i][:3] == "***":
            if textblocks[i+1][:3] == "~~~":
                print("replace", i, normal[n_index], textblocks[i:i+2])
            else:
                print("insert", i, normal[n_index], textblocks[i])
                insert(textblocks, i, markdown)
        else:
            n_index +=1
        i +=1

    # insertion on its own
    # insertion next to a deletion

def main():
    # Pull the markdown from master
    markdown = readMarkdown()

    # Identify which text has stayed the same and which has changed
    text = findChanges("./word/document.xml")
    groupBlocks(text, markdown)

main()

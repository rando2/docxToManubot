import re
import argparse
import xml.etree.ElementTree as ET
import pysbd
from fuzzywuzzy import fuzz

def readMarkdown(mdfile):
    with open(mdfile, 'r') as origFile:
        # Read & format original markdown
        origTextRaw = origFile.read()
        origText = origTextRaw.splitlines()
        origText = [t.strip() for t in origText]
        return origText

def writeMarkdown(text, fout):
    with open(fout, 'w') as editedFile:
        for line in text:
            # Add an extra space before new sections
            if line[:3] == "###":
                editedFile.write('\n')
            editedFile.write(line + '\n')
    print("Wrote {}".format(fout))

def cleanAnnotations(text):
    text = text.replace("~~~", "")
    text = text.replace("***", "")
    return text

def cleanMarkdown(text):
    text = text.replace(" #", "\n\n#")
    text = text.replace("  ", "\n")
    return splitSentences(text)

def splitSentences(text):
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def extractChangesXML(xmlFile):
    """Evaluates an XML file generated from a docx file to extract the text including
    insertions and deletions added with track changes"""
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
    """Want to replace the minimum number of characters possible to avoid issues
    with references, manubot & HTML formatting, etc."""
    markdown_text = " ".join(markdown[mdi[0]: mdi[1]+1])
    for blockIndex in range(0,len(textblocks)):
        if textblocks[blockIndex][:3] not in ["~~~", "***"]:
            # Skip text that was not edited
            continue
        elif blockIndex > 0 and textblocks[blockIndex - 1][:3] not in ["~~~", "***"]:
            # If there is unedited text before
            if textblocks[blockIndex][:3] == "~~~":
                # For deletions, original text is the leading text + deleted content
                original_text = "".join(textblocks[blockIndex - 1:blockIndex + 1])
            elif textblocks[blockIndex][:3] == "***":
                # For insertions, original text is just leading text
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
    markdown[mdi[0]:mdi[1]+1] = cleanMarkdown(markdown_text)
    return markdown

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
    return modifyText(textblocks, markdown, markdown_bounds)

def groupTextBlocks(textblocks, markdown):
    """Use the mark-up in the textblocks list to determine whether we are deleting, inserting
    or replacing text. To do this, pull the most recent normal block"""
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

def main(args):
    # Read in the markdown pulled from upstream
    markdown = readMarkdown(args.base_markdown)

    # Identify which text has stayed the same and which has changed
    text = extractChangesXML("{}/document.xml".format(args.documentXMLDir))

    # Begin analyzing the text blocks identified in the XML
    # Locate each in the markdown file and replace the old text with updated text
    edited_markdown = groupTextBlocks(text, markdown)
    writeMarkdown(edited_markdown, args.tempDocxMD)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('base_markdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    parser.add_argument('documentXMLDir',
                        help='Directory containing the document.xml file generated when docx is unzipped',
                        type=str)
    parser.add_argument('tempDocxMD',
                        help='Path to write the markdown file generated from the docx',
                        type=str)
    args = parser.parse_args()
    main(args)

import re
import argparse
import xml.etree.ElementTree as ET
from textFunctions import *

def trimTextblocks(textblocks, endOfBody):
    """Remove blocks of text from the list that are from the front matter or back matter
    Input: list of text blocks extracted from XML file
    Returns: list of text blocks expected to be found in corresponding markdown file"""
    title = [textblocks[0]]
    body = list()
    for i in range(1, len(textblocks)):
        letters = re.sub(r'[^a-zA-Z]', '', textblocks[i])
        if letters == "Abstract": # add the preceeding number too
            body+= textblocks[i-1:i+1]
        elif letters == endOfBody.replace(" ", ""):
            body = body[:-1] # remove preceding number
            break
        elif letters == "References": #fail safe to stop back matter from populating
            body = body[:-1] # remove preceding number
            break
        elif len(body) > 0:
            body.append(textblocks[i])
    return title + body

def manualNamespace(tag, nsmap):
    """Manually apply a namespace to a tag. There is probably a command to do this but
    I haven't been able to find it
    Input: tag (string), namespace map (dictionary mapping alias (w) to url)
    Returns: tag (string)"""
    for nskey, nsvalue in nsmap.items():
        tag = tag.replace("{" + nsvalue + "}", nskey + ":")
    return tag

def readXML(xmlFile):
    """Read the XML file generated from a docx file to extract the text including
    insertions and deletions added with track changes
    Input: string indicating path of XML file
    Returns: list of blocks of text from XML file"""
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
            # To do: how to map a tag onto the namespace?
            tag = manualNamespace(section.tag, nsmap)
            if tag in ["w:hyperlink", "w:bookmarkStart", "w:bookmarkEnd", "w:pPr"]:
                continue
            if len(section.attrib) == 0: # feels arbitrary but this is one way to catch ins
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

def main(args):
    # Identify which text has stayed the same and which has changed
    text = readXML("{}/word/document.xml".format(args.documentXMLDir))
    text = trimTextblocks(text, args.endOfBody)
    writeList(text, "textblocks.txt")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('documentXMLDir',
                        help='Directory containing the document.xml file generated when docx is unzipped',
                        type=str)
    parser.add_argument('endOfBody',
                        help='Optional string identifying the text that signifies the end of the body',
                        default="References",
                        type=str)
    args = parser.parse_args()
    main(args)

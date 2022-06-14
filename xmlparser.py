import xml.etree.ElementTree as ET
import docx #may be able to use normal version?
import pysbd

def readDocx(filename):
    """Read the paragraphs of the docx file in as a list.
    These will contain deletions but not insertions due to a quirk of python-docx
    Input: name of docx file
    Returns: list of paragraph text """
    paragraphs = []
    document = docx.Document(filename)
    docPos = "head"
    for para in document.paragraphs:
        if docPos == "head":
            if "Abstract" in para.text:
                docPos = "body"
                continue # remove this!
            else:
                continue
        if "Additional Items" in para.text:
            return
        paragraphs.append(para.text)
    return(paragraphs)

def readMarkdown():
    with open("origmdMD.md", 'r') as origFile:
        # Read & format original markdown
        origTextRaw = origFile.read()
        origText = origTextRaw.splitlines()
        origText = [t.strip() for t in origText]
        #print(origText)

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

def insert(textblocks, i, markdown):
    

def replaceLines(textblocks, markdown):
    """Use the mark-up in the textblocks list to determine whether we are deleting, inserting
    or replacing text."""
    i = 0
    while i < len(textblocks):
        if textblocks[i][:3] == "~~~":
            if textblocks[i+1][:3] == "***":
                print("replace", textblocks[i:i+2])
            else:
                print("delete", textblocks[i])
        elif textblocks[i][:3] == "***":
            if textblocks[i+1][:3] == "~~~":
                print("replace", textblocks[i:i+2])
            else:
                print("insert", textblocks[i])
        i +=1

    # insertion on its own
    # insertion next to a deletion

def main():
    # Pull the markdown from master
    markdown = readMarkdown()

    # Identify which text has stayed the same and which has changed
    text = findChanges("./word/document.xml")
    replaceLines(text, markdown)

main()

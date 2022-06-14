import xml.etree.ElementTree as ET
import docx #may be able to use normal version?
import pysbd

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
    print("INSERT")
    # Find match to last normal block in markdown
    normal = [blockIndex for blockIndex in range(len(textblocks)) if
              textblocks[blockIndex][:3] not in ["~~~", "***"]]
    last_normal = max([blockIndex for blockIndex in normal if blockIndex < i])
    next_normal = min([blockIndex for blockIndex in normal if blockIndex > i])
    print(last_normal, next_normal, textblocks[last_normal],
          "".join(textblocks[last_normal+1:next_normal]),
          textblocks[next_normal])

    # if n == 0

def replaceLines(textblocks, markdown):
    """Use the mark-up in the textblocks list to determine whether we are deleting, inserting
    or replacing text."""
    i = 0
    normal = [i for i in range(len(textblocks)) if textblocks[i][:3] not in ["~~~", "***"]]
    n_index = 0
    print(normal)
    while i < len(textblocks):
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
    replaceLines(text, markdown)

main()

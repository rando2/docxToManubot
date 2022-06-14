import xml.etree.ElementTree as ET
import docx #may be able to use normal version?

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

def findChanges(xmlFile):
    """Inspired by N. Fisher: https://stackoverflow.com/questions/61316140/extracting-data-from-xml-of-docx-document"""
    tree = ET.parse(xmlFile)
    root = tree.getroot()

    # Declare namespace dictionary
    nsmap = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    # Iterate through body
    for child in root[0]:
        insertions = child.findall('.//w:ins', nsmap)
        if len(insertions) > 0:
            for i in insertions:
                for j in i.findall('.//w:t', nsmap):
                    continue
                    print(j.text, j.tag)
        else:
            print(child.attrib)
            continue
            for i in child.findall('.//w:r//w:t', nsmap):
                print(i.text)
                continue
                if len(i.text) > 0:
                    print(i.text)
                else:
                    print('except')
                    print(i.findall('.//w:t', nsmap))


    """"#loop through all w:t tags and append their values to list
    for i in root.findall('.//w:r//w:t', nsmap):
        for j in root.findall('.//w:ins', nsmap):
        for j in i.findall('.//w:t', nsmap):
            print(j.text)
        #print(i.attrib, i.text, i.tag, i.text)
    """

readDocx("test.docx")
findChanges("./word/document.xml")

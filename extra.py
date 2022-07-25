from xml.dom.minidom import parse
import markdown
from bs4.dammit import EntitySubstitution
import xml.etree.ElementTree as ET
import pysbd
import os
import re
import argparse
import docx
from lxml import etree
import zipfile

seg = pysbd.Segmenter(language="en", clean=False)

def get_word_xml(docx_filename):
    document = parse("/Users/halierando/Downloads/file-content/word/document.xml")
    return document

def _itertext(self, my_etree):
    """Iterator to go through xml tree's text nodes"""
    for node in my_etree.iter(tag=etree.Element):
        if self._check_element_is(node, 't'):
            yield (node, node.text)

def get_xml_tree(xml_string):
   return etree.fromstring(xml_string)

def _check_element_is(self, element, type_char):
    word_schema = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    return element.tag == '{%s}%s' % (word_schema, type_char)

def xpath():
    xml_from_file = get_word_xml('./diagnostics-manuscript(1).docx')
    xml_tree = get_xml_tree("/Users/halierando/Downloads/file-content/word/document.xml")
    for node, txt in xml_tree._itertext():
        print(txt)

def readTC():
    document = parse("/Users/halierando/Downloads/file-content/word/document.xml")
    text = document.getElementsByTagNameNS("*", "ins")
    for element in text:
        print(element)
        print(element.attributes)
        print(element.childNodes)
        exit(0)

def readDocx():
    document = docx.Document('diagnostics-manuscript(1).docx')
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
        print(para.inserted_text)

def greekToHTML(char):
    # From https://stackoverflow.com/questions/701704/convert-html-entities-to-unicode-and-vice-versa
    escaper = EntitySubstitution()
    return escaper.substitute_html(char)

def formatSection(section):
    try:
        heading = section.splitlines()[0]
    except IndexError:
        print("error:", section)
        return

    # How many pound signs should be here?
    # Split on "##" so need to add two back in to each section
    headingHTML = re.search(r'(#+)',heading)
    try:
        levelNum = len(headingHTML.group(0))+3
    except AttributeError:
        levelNum = 3
    sectionLevel = levelNum * "#"

    # Grab the title
    sectionTitle = re.search(r'\s([^0-9#.][^#.]+)',heading).group(0)

    # Reformat the section
    newSection = " ".join([sectionLevel, sectionTitle])
    newSection = "".join([newSection, section.replace(heading, "")])
    return newSection

#def diffText(orig, mod):
    # use XML file to locate sentence that is changed & proposed change

def main(args):
    with open("origmdMD.md", 'r') as origFile, open("docx-to-manubot-tmp/docxMD.md", "r") as edFile:
        # Read & format original markdown
        origTextRaw = origFile.read()
        origText = origTextRaw.splitlines()
        origText = [t.strip() for t in origText]

        # Read & extract text from after title ("##") through to start of back matter ("Additional Items")
        edTextRaw = edFile.read()
        title = edTextRaw.split("title: ")[1].splitlines()[0]
        edTextBody = edTextRaw.split("# 1 Additional Items")[0].split("##")[1:]
        #Move the second split out and in between need to replace greek symbols, bold/it, etc

        xpath()
        exit(0)
        header = " ".join(["##",title])
        header += "\n\n"
        body = "".join([formatSection(t) for t in edTextBody if len(t) > 0])
        body = seg.segment(body)

        # For some reason, join won't work on this list with an empty string (it should!)
        # I don't know if pysbd is returning a list with a weird property
        # But this fix, if questionable, does work. 289347983274 seems unlikely to appear organically
        edText = header + "289347983274".join(body)
        edText = edText.replace(" 289347983274", "\n")
        edText = edText.replace("289347983274", "")
# Text changes to make

#1 greek letters
#print(greekToHTML("μ"))
# To construct regex to detect these, see:
# https://stackoverflow.com/questions/62592750/python-regex-greek-characters

#2 bold and italics

# 3 split sentences

def findChanges(xmlFile):
    """Inspired by N. Fisher: https://stackoverflow.com/questions/61316140/extracting-data-from-xml-of-docx-document"""
    tree = ET.parse(xmlFile)
    root = tree.getroot()

    # Declare namespace dictionary
    nsmap = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    # Create a dictionary of all insertions by their rsidR
    # The rsidR is fixed for
    insertions = dict()
    for ins in root[0].findall('.//w:ins', nsmap):
        insID = ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        for data in ins.findall('.//w:r', nsmap):
            rsidR = data.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rsidR')
            insertions[rsidR] = insertions.get(rsidR, dict())
            for idata in data.findall('.//w:t', nsmap):
                insertedText = idata.text
                insertions[rsidR][insID] = insertedText
    print(insertions)

def old():
    for child in root[0].findall('.//w:p', nsmap):  # each paragraph
        #print(child.tag, child.attrib, child.findall('.//w:*', nsmap))
        insertions = child.findall('.//w:ins', nsmap)

        print(child.get("w:rsidR", nsmap))
        if len(insertions) > 0:
            for i in insertions:
                print(i.attrib)
                print(i.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rsidR'))
                #print(i.attrib)
                #for j in i.findall('.//w:t', nsmap):
                #    print(j.text, j.tag)
        #continue
        """else:
            print([c.text for c in child.findall('.//w:t', nsmap)])
            continue
            for i in child.findall('.//w:r//w:t', nsmap):
                print(i.text)
                continue
                if len(i.text) > 0:
                    print(i.text)
                else:
                    print('except')
                    print(i.findall('.//w:t', nsmap))"""


    """"#loop through all w:t tags and append their values to list
    for i in root.findall('.//w:r//w:t', nsmap):
        for j in root.findall('.//w:ins', nsmap):
        for j in i.findall('.//w:t', nsmap):
            print(j.text)
        #print(i.attrib, i.text, i.tag, i.text)
    """

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser.add_argument('update_json',
    #                    help='Path of the JSON file with extracted statistics',
    #                    type=str)
    #parser.add_argument('platform_types',
    #                   help='Path of the CSV file with the vaccine to platform mapping',
    #                   type=str)
    args = parser.parse_args()
    main(args)




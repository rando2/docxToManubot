from xml.dom.minidom import parse
import markdown
from bs4.dammit import EntitySubstitution
import pysbd
import os
import re
import argparse
import docx

seg = pysbd.Segmenter(language="en", clean=False)

def readTC():
    document = parse("/Users/halierando/Downloads/file-content/word/document.xml")
    text = document.getElementsByTagNameNS("*", "ins | del")
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
        print(para.accepted_text)

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
    with open("origmdMD.md", 'r') as origFile, open("docxMD.md", "r") as edFile:
        # Read & format original markdown
        origTextRaw = origFile.read()
        origText = origTextRaw.splitlines()
        origText = [t.strip() for t in origText]

        # Read & extract text from after title ("##") through to start of back matter ("Additional Items")
        edTextRaw = edFile.read()
        title = edTextRaw.split("title: ")[1].splitlines()[0]
        edTextBody = edTextRaw.split("# 1 Additional Items")[0].split("##")[1:]
        #Move the second split out and in between need to replace greek symbols, bold/it, etc

        readDocx()
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




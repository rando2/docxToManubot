import pysbd
import re

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
            editedFile.write(line)
    print("Wrote {}".format(fout))

def cleanMarkdown(text):
    text = text.replace(" #", "\n\n#")
    text = text.replace("  ", "\n")
    return splitSentences(text)

def cleanAnnotations(text):
    text = text.replace("[-", "")
    text = text.replace("-]", "")
    text = text.replace("{+", "")
    text = text.replace("+}", "")
    return text

def splitSentences(text):
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def findNextNormal(textblocks, i):
    """Increment forward until find the next normal block"""
    while i < len(textblocks):
        i += 1
        if textblocks[i][:3] not in ["~~~", "***"]:
            if not re.search(r"\[-|-\]|\{\+|\+\}", textblocks[i]):
                return i
    return -1

def findLastNormal(textblocks, i):
    """Increment backwards until find the last normal block"""
    while i >= 0:
        i -= 1
        if not re.search(r"\[-|-\]|\{\+|\+\}", textblocks[i]):
            return i
    return -1

def reconstructOrig(text):
    # Find references and track changes metadata
    annotations = re.compile(r" \{\+.*?\+\}| \\\[\[[0-9]+[^A-Za-z]*\\\]")
    text = re.sub(annotations, "", text)
    # Can have some stray metadata because of linebreaks
    text = re.sub("\[(.*?\].*?)\}(.*?)\+\}", "", text)
    text = re.sub("\[.*?\]\{.*\}", "", text)
    # Remove the annotations around deletions
    text = re.sub("-\]|\[-", "", text)
    return text

def reformatMarkdown(markdown):
    paragraphs = list()
    currentPara = []
    for line in markdown:
        # Remove markdown comments that won't appear in docx
        line = re.sub("<!--.*?-->+", "", line)
        currentPara.append(line)
        # look for lines that are only whitespace
        if not re.search(r"\S", line):
            paragraphs.append(" ".join(currentPara))
            currentPara = []
    return paragraphs

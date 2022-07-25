import pysbd

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

def cleanMarkdown(text):
    text = text.replace(" #", "\n\n#")
    text = text.replace("  ", "\n")
    return splitSentences(text)

def cleanAnnotations(text):
    text = text.replace("~~~", "")
    text = text.replace("***", "")
    return text

def splitSentences(text):
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def writeList(text, fout):
    print("writing", fout)
    with open('docx-to-manubot-tmp/' + fout, 'w') as filehandle:
        filehandle.writelines("%s\n" % block for block in text)

def findNextNormal(textblocks, i):
    """Increment forward until find the next normal block"""
    while i < len(textblocks):
        i += 1
        if textblocks[i][:3] not in ["~~~", "***"]:
            return i
    return -1

def findLastNormal(textblocks, i):
    """Increment backwards until find the last normal block"""
    while i >= 0:
        i -= 1
        if textblocks[i][:3] not in ["~~~", "***"]:
            return i
    return -1

def splitSentences(text): #may be able to remove?
    seg = pysbd.Segmenter(language="en", clean=True)
    return seg.segment(text)

def cleanMarkdown(text):
    text = text.replace(" #", "\n\n#")
    text = text.replace("  ", "\n")
    return splitSentences(text)

def writeMarkdown(text, fout):
    with open(fout, 'w') as editedFile:
        for line in text:
            # Add an extra space before new sections
            if line[:3] == "###":
                editedFile.write('\n')
            editedFile.write(line + '\n')
    print("Wrote {}".format(fout))

writeMarkdown(edited_markdown, args.tempDocxMD)

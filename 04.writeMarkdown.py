from textFunctions import *
import argparse
import ast

# Read in list of lists indicating the ranges of indices that correspond to edits
# from 01. and 02.
def modifyText(textblocks, markdown, mdi):
    """Want to replace the minimum number of characters possible to avoid issues
    with references, manubot & HTML formatting, etc."""

    # Ensure these are paragraphs with spaces between sentences (can be lost due to trimming)
    # and clean up the annotations (~~~ and ***)
    original_text = " ".join(splitSentences(original_text))
    original_text = cleanAnnotations(original_text)

    edited_text = " ".join(splitSentences(edited_text))
    edited_text = cleanAnnotations(edited_text)

    print("O:", original_text)
    print("E:", edited_text)
    exit(0)
    # pull the corresponding text in markdown
    numSentences = len(splitSentences("".join(textblocks)))
    markdown_text = " ".join(markdown[mdi:mdi+numSentences])
    markdown_text = markdown_text.replace(original_text, edited_text)
    markdown = markdown[:mdi] + \
                      cleanMarkdown(markdown_text) + \
                      markdown[mdi+len(original_text):]
    return markdown

def main(args):
    # Read in the files generated in the previous 3 steps
    with open('docx-to-manubot-tmp/textblocks.txt', 'r') as filehandle:
        textblocks = filehandle.readlines()
    with open('docx-to-manubot-tmp/matchIndices.txt', 'r') as filehandle:
        matchIndices = [block.rstrip() for block in filehandle.readlines()]

    # Read in the markdown pulled from upstream
    markdown = readMarkdown(args.baseMarkdown)

    for positions in matchIndices:
        start, stop, mdPos = [int(i) for i in ast.literal_eval(positions)]
        print(start, stop, mdPos)
        continue

        markdown = modifyText(textblocks[start:stop+1], markdown, mdPos)

    #print("Writing", args.mdOutput)
    #writeMarkdown(markdown, args.mdOutput)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseMarkdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    parser.add_argument('mdOutput',
                        help='Path of the md file where the edited markdown text will be stored',
                        type=str)
    args = parser.parse_args()
    main(args)

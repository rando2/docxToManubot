from textFunctionsDiff import *
import argparse

def main(args):
    text = readMarkdown(args.markdownFile)
    new_text = list()
    for t in text:
        if "." in t:
            new_text = new_text + splitSentences(t)
        else:
            new_text = new_text + [t]
    writeMarkdown(new_text, args.markdownFile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('markdownFile',
                        help='Path of the md file to be cleaned',
                        type=str)
    args = parser.parse_args()
    main(args)

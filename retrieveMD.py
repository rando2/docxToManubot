import re
import argparse
import requests

def main(args):
    with open(args.mdFromDocx, 'r') as markdownFile:
        fullText = markdownFile.read()
        lines = fullText.splitlines()
        for line in lines:
            if "permalink" in line:
                pattern = 'was automatically generated from \[(\S*)\]'
                linkText = re.search(pattern, line)
                commitID = linkText.group().split("@")[1]
                commitID = commitID.replace("]","")
                url = "https://raw.githubusercontent.com/{}}/{}/content/{}".format(
                    args.upstreamRep, commitID, args.upstreamMD)
                upstreamMD = requests.get(url)
                with open(args.tempUpstreamMD, 'wb') as fout:
                    fout.write(upstreamMD.content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('upstreamRep',
                        help='Location of the upstream repository, e.g., greenelab/covid19-review',
                        type=str)
    parser.add_argument('upstreamMD',
                        help='Name of the upstream markdown file, e.g., 10.diagnostics.md',
                        type=str)
    parser.add_argument('mdFromDocx',
                        help='Name of the markdown file generated from the docx',
                        type=str)
    parser.add_argument('tempUpstreamMD',
                        help='Where to save the markdown file retrieved from upstream',
                        type=str)
    args = parser.parse_args()
    main(args)

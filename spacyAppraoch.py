"""Code copied and adapted from https://towardsdatascience.com/natural-language-processing-document-search-using-spacy-and-python-820acdf604af"""
import spacy
from spacy.matcher import PhraseMatcher
from scipy import spatial
import argparse
import re
import ast
from textFunctions import *

# create spacy document object
def getSpacyDocument(markdown, nlp):
    main_doc = nlp(markdown)  # create spacy document object
    return main_doc

def createKeywordsVectors(change, nlp):
    doc = nlp(change)  # convert to document object
    return doc.vector

# method to find cosine similarity
def cosineSimilarity(vect1, vect2):
    # return cosine distance
    return 1 - spatial.distance.cosine(vect1, vect2)

# method to find similar words
def getSimilarWords(keyword, nlp):
    similarity_list = []

    keyword_vector = createKeywordsVectors(keyword, nlp)

    for tokens in nlp.vocab:
        if (tokens.has_vector):
            if (tokens.is_lower):
                if (tokens.is_alpha):
                    similarity_list.append((tokens, cosineSimilarity(keyword_vector, tokens.vector)))

    similarity_list = sorted(similarity_list, key=lambda item: -item[1])
    similarity_list = similarity_list[:30]

    top_similar_words = [item[0].text for item in similarity_list]

    top_similar_words = top_similar_words[:3]
    top_similar_words.append(keyword)

    for token in nlp(keyword):
        top_similar_words.insert(0, token.lemma_)

    for words in top_similar_words:
        if words.endswith("s"):
            top_similar_words.append(words[0:len(words) - 1])

    top_similar_words = list(set(top_similar_words))

    #d = enchant.Dict()
    #top_similar_words = [words for words in top_similar_words if d.check(words) == True]

    return ", ".join(top_similar_words)

# method for searching keyword from the text
def search_for_keyword(keyword, doc_obj, nlp):
    phrase_matcher = PhraseMatcher(nlp.vocab)
    phrase_list = [nlp(keyword)]
    phrase_matcher.add("Text Extractor", None, *phrase_list)

    matched_items = phrase_matcher(doc_obj)
    print(matched_items)
    matched_text = []
    for match_id, start, end in matched_items:
        text = nlp.vocab.strings[match_id]
        span = doc_obj[start: end]
        matched_text.append(span.sent.text)

def main(args):
    # spacy english model (large)
    nlp = spacy.load('en_core_web_lg')

    with open("tmp/upstream.md", 'r') as upstreamFile:
        markdown = upstreamFile.read()
        markdown = getSpacyDocument(markdown, nlp)

    with open(args.tempTextblocks, 'r') as filehandle:
        textblocks = filehandle.readlines()
    with open(args.tempIndices, 'r') as filehandle:
        textToEval = [block.rstrip() for block in filehandle.readlines()]

    # Examining each paragraph that contains edits
    companionParas = list()
    startPara = 0
    runData = None
    previous = 0
    for indexNum in range(0, len(textToEval)):
        # Evaluate the list of lists of indices & retrieve the corresponding blocks of text
        start, stop = [int(i) for i in ast.literal_eval(textToEval[indexNum])]

        # If the last block lacked enough text to match, then adjust the span here
        if previous == 1:
            start = int(ast.literal_eval(textToEval[indexNum-1])[0])

        # Pull text in the range of the indices
        text = " ".join(textblocks[start:stop])

        changesWithinBlock = []
        change = re.compile("(\[-.+?-\]*) (\{\+.*?\+\})")
        for match in re.finditer(change, text):
            square = re.search("(\[-.+?-\]*)", match.group())
            if len(changesWithinBlock) == 0:
                normalText = text[0: match.start()] + square.group()
            else:
                normalText = text[changesWithinBlock[-1][1]: match.start()] + square.group()

            normalText = normalText.replace("[-", "")
            normalText = normalText.replace("-]", "")

            if len(re.findall("(\w+)", normalText)) >= 5:
                print(normalText)
                # Need to handle this by adding the edited text too
                #print("problem:", normalText)
                #similar_keywords = getSimilarWords(normalText, nlp)
                search_for_keyword(normalText, markdown, nlp)
                exit(0)

            changesWithinBlock.append((match.start(), match.end()))
            #print(match.group(), normalText)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('baseMarkdown',
                        help='Path of the md file from upstream the docx will be compared against',
                        type=str)
    parser.add_argument('tempTextblocks',
                        help='temp text file to store textblocks pulled from diff',
                        type=str)
    parser.add_argument('tempIndices',
                        help='temp text file to store indices of changes pulled from diff',
                        type=str)
    parser.add_argument('matchedPara',
                        help='temp text file to store corresponding docx and upstream text',
                        type=str)
    args = parser.parse_args()
    main(args)


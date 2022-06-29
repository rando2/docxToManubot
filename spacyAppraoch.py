"""Guided by https://towardsdatascience.com/natural-language-processing-document-search-using-spacy-and-python-820acdf604af"""
import spacy

# customer sentence segmenter for creating spacy document object
def setCustomBoundaries(doc):
    # traversing through tokens in document object
    for token in doc[:-1]:
        if token.text == ';':
            doc[token.i + 1].is_sent_start = True
        if token.text == ".":
            doc[token.i + 1].is_sent_start = False
    return doc

# create spacy document object from pdf text
def getSpacyDocument(markdown, nlp):
    main_doc = nlp(markdown)  # create spacy document object
    return main_doc

def createChangeVectors(change, nlp):
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

    top_similar_words = [words for words in top_similar_words if enchant_dict.check(words) == True]

    return ", ".join(top_similar_words)


# spacy english model (large)
nlp = spacy.load('en_core_web_lg')
# adding setCusotmeBoundaries to the pipeline
nlp.add_pipe(setCustomBoundaries, before='parser')

with open("tmp/upstream.md", 'r') as upstreamFile:
    markdown = upstreamFile.read()
    getSpacyDocument(markdown, nlp)
keywords = ['slowing down the global pandemic']
similar_keywords = getSimilarWords(keywords, nlp)

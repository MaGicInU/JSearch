import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize


def getVerbs(text):
    if text == "":
        return []
    stop_words = set(stopwords.words('english'))
    tokenized = sent_tokenize(text)
    for i in tokenized:
        wordsList = nltk.word_tokenize(i)
        wordsList = [w for w in wordsList if not w in stop_words]
        tagged = nltk.pos_tag(wordsList)
        verbs = []
        for tup in tagged:
            if "VB" in tup[1] or "NN" in tup[1]:
                verbs.append(tup[0])
        return verbs


def getSynonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lm in syn.lemmas():
            synonyms.append(lm.name().replace("_", " ").replace("-", " "))
    return synonyms


def getProcessedQueryText(queryText="How can I export elasticsearch index to my local computer from server and import it to another sever like we do from phpMyadmin for mysql database"):
    verbs = getVerbs(queryText)
    verbSynPair = []
    for verb in verbs:
        synList = getSynonyms(verb)
        verbSynPair.append([verb, list(set(synList))])
    additionalText = ""
    for pair in verbSynPair:
        additionalText += pair[0]+" "+" ".join(pair[1])

    return queryText+additionalText

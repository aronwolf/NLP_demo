import sys; sys.path.insert(0, "..")
#import nltk
import spacy

def noun_extract(text):
#    grammar = r"""
#    NP: {<DT>? <JJ>* <NN>*} # NP
#    P: {<IN>}           # Preposition
#    V: {<V.*>}          # Verb
#    PP: {<P> <NP>}      # PP -> P NP
#    VP: {<V> <NP|PP>*}  # VP -> V (NP|PP)*
#    """

    noun_array = []

    nlp = spacy.load("en")
    doc = nlp(text)
    for np in doc.noun_chunks:
        noun_array.append(np.text)
       
#    tagged = nltk.pos_tag(nltk.word_tokenize(text))
#
#    noun_list = []
#    for t in range(len(tagged)):
#        if ("NN" in tagged[int(t)][1]) | ("JJ" in tagged[int(t)][1]):
#            noun_list.append(tagged[int(t)][0])
#
#        elif ("IN" in tagged[int(t)][1]) & (len(noun_list) > 0):
#            noun_list.append(tagged[int(t)][0])
#
#        else:
#            if len(noun_list) > 0:
#                if tagged[int(t-1)][1] == "IN":
#                    noun_list.pop()
#                noun_array.append(noun_list)
#            noun_list = []

    return noun_array

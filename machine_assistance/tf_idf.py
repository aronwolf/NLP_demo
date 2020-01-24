import sys; sys.path.insert(0, "..")
import utils.file_io as file_io
import utils.tokenize_statements as tokenize_statements
import os
import json
import pandas as pd
import pickle
import sklearn.feature_extraction.text


#def tf_idf_fit(text, vocab_json='../data/machine_assistance/wiki_and_concept_term_vocabulary.json'):
def tf_idf_fit(text, vocab_json='../data/machine_assistance/business_concept_term_vocabulary.json'):
#def tf_idf_fit(text, vocab_json='../data/machine_assistance/social_studies_concept_term_vocabulary.json'):
#def tf_idf_fit(text, vocab_json='../data/machine_assistance/language_arts_concept_term_vocabulary.json'):
#def tf_idf_fit(text, vocab_json='../data/machine_assistance/science_concept_term_vocabulary.json'):
    with open(vocab_json) as vocab_file:
        vocab = json.load(vocab_file)

    my_stop_words = sklearn.feature_extraction.text.ENGLISH_STOP_WORDS.union(['Analyze', 'Assess', 'Compare', 'Contrast', 'Debate', 'Define', 'Demonstrate', 'Describe', 'Detect', 'Determine', 'Discuss', 'Distinguish', 'Evaluate', 'Examine', 'Explain', 'Explore', 'Identify', 'Illustrate', 'Interpret', 'Investigate', 'Show', 'Specify', 'Summarize', 'Trace', 'Understand', 's', 'u', 'x', '1'])

    tokenized_text = tokenize_statements.tokenize(text)

    tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer(vocabulary=vocab, max_df=0.80, min_df=1, stop_words=set(my_stop_words), encoding='ascii', decode_error='ignore', lowercase=True, ngram_range=(1,5), token_pattern=r'\b\w+\b')

    tfidf = tfidf_vectorizer.fit_transform(tokenized_text)
    vocab_filename = os.path.split(vocab_json)[1]
    vocab_filename = vocab_filename.split('.')[0]
    pickle.dump(tfidf ,open('../data/machine_assistance/%s_matrix.pickle' % vocab_filename, 'wb'))
    pickle.dump(tfidf_vectorizer, open('../data/machine_assistance/%s_vectorizer.pickle' % vocab_filename, 'wb'))
    return tfidf


#def tf_idf_transform(text, vectorizer_file = '../data/machine_assistance/wiki_and_concept_term_vocabulary_vectorizer.pickle'):
def tf_idf_transform(text, vectorizer_file = '../data/machine_assistance/business_concept_term_vocabulary_vectorizer.pickle'):
#def tf_idf_transform(text, vectorizer_file = '../data/machine_assistance/social_studies_concept_term_vocabulary_vectorizer.pickle'):
#def tf_idf_transform(text, vectorizer_file = '../data/machine_assistance/language_arts_concept_term_vocabulary_vectorizer.pickle'):
#def tf_idf_transform(text, vectorizer_file = '../data/machine_assistance/science_concept_term_vocabulary_vectorizer.pickle'):
    tokenized_text = tokenize_statements.tokenize(text)
    tfidf_vectorizer = pickle.load(open(vectorizer_file, "rb" ))
    tfidf = tfidf_vectorizer.transform(tokenized_text)
    return tfidf


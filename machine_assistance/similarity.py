import sys; sys.path.insert(0, "..")                                   
import utils.file_io as file_io
import machine_assistance.tf_idf as tf_idf 
import pandas as pd                          
from sklearn.metrics.pairwise import linear_kernel
import utils.tokenize_statements as tokenize_statements
import sklearn.feature_extraction.text
import json
import re


def sim(sim_index, sample1, sample2, tfidf, subject, filter = False):
    vocab_json='../data/machine_assistance/%s_concept_term_vocabulary.json' % subject
#    vocab_json='../data/machine_assistance/wiki_and_concept_term_vocabulary.json'
#    vocab_json='../data/machine_assistance/business_concept_term_vocabulary.json'
#    vocab_json='../data/machine_assistance/social_studies_concept_term_vocabulary.json'
#    vocab_json='../data/machine_assistance/language_arts_concept_term_vocabulary.json'
#    vocab_json='../data/machine_assistance/science_concept_term_vocabulary.json'
    with open(vocab_json) as vocab_file:
        vocab = json.load(vocab_file)

    sample_tfidf = tf_idf.tf_idf_transform(sample2.LearningStatement, '../data/machine_assistance/%s_concept_term_vocabulary_vectorizer.pickle' % subject)

#    print "Building boost array"
#    features = file_io.read_xlsx('../data/machine_assistance/features.xlsx')
##    topic_array = features.ConceptTerm
#    unprocessed_topic_array = list(tokenize_statements.tokenize(features.ConceptTerm))
#    topic_array = []
#    for topic in unprocessed_topic_array:
#        topic = re.sub('(\[u\')','', topic)
#        topic = re.sub('(\',)','', topic)
#        topic = re.sub('(u\')','', topic)
#        topic = re.sub('(\'\])','', topic)
#        topic_array.append(topic)
#
#    word_array = []
#    boost_array = []
##    for x in range(sample_tfidf.shape[0]):
#    for r in range(sample_tfidf[0].shape[0]):
#        for ind in range(sample_tfidf[0].indptr[r], sample_tfidf[0].indptr[r+1]):
#            word_array.append(sample_tfidf[0].indices[ind])
#
#    try:
#        for i in range(len(topic_array)):
#            if vocab[topic_array[i]] in word_array:
#                boost_array.append(vocab[topic_array[i]])
#    except:
#        pass
#
#    for i in boost_array:
#        print "Applying boost"
#        sample_tfidf[0,i] = sample_tfidf[0,i]*1.5
#

    sample_doc_index = 0

    df = pd.DataFrame(columns=['LearningStatement_1', 'LearningStatement_2', 'SimilarityIndex', 'SimilarityCount', 'Suggest'])
#    for doc_vector in sample_tfidf:
#        cosine_similarities = linear_kernel(doc_vector, tfidf).flatten()
    cosine_similarities = linear_kernel(sample_tfidf, tfidf).flatten()
    related_docs_indices_short_list = sorted(x for x in cosine_similarities if x > sim_index)
    related_docs_indices_short_list_length = int(len(related_docs_indices_short_list))
    related_docs_indices = cosine_similarities.argsort()[:-10:-1]
    for index in related_docs_indices:
        if cosine_similarities[index] > sim_index:
            suggest = 1
        else:
            suggest = 0
        try:
            row_data = [sample2.iloc[sample_doc_index]['LearningStatement'].rstrip(), sample1.iloc[index]['LearningStatement'].rstrip(), cosine_similarities[index], related_docs_indices_short_list_length, suggest]
        except:
            row_data = [sample2.iloc[sample_doc_index]['LearningStatement'].rstrip(), sample1.iloc[index]['LearningStatement'].rstrip(), cosine_similarities[index], related_docs_indices_short_list_length, suggest]
        df.loc[len(df.index)] = row_data
#        sample_doc_index += 1

    dedup_df = df.drop_duplicates(keep = 'first')
    dedup_df[list(['SimilarityCount', 'Suggest'])] = dedup_df[list(['SimilarityCount', 'Suggest'])].astype(int)
    if filter:
        mask = dedup_df['Suggest'].isin([1])
        return_df = dedup_df[mask]
        return return_df
    else:
        return dedup_df

def suggest(sim_index, sample1, sample2, tfidf, subject, filter = False):
    df_full = sim(sim_index, sample1, sample2, tfidf, subject, filter = False)

    mask = df_full['Suggest'].isin([1])
    suggest_df = df_full[mask]
    if suggest_df.empty:
        return suggest_df, sample2
    return suggest_df, pd.DataFrame()


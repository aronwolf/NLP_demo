import sys; sys.path.insert(0, "..")                                   
sys.path.insert(0, "../machine_assistance/")                            
import utils.file_io as file_io                                         
import pandas as pd                                                     
import similarity                                                       
import tf_idf   
import re
import nltk
import pickle
from py2neo import Graph 
from bs4 import BeautifulSoup

subject = sys.argv[3]
with open(sys.argv[1]) as fp:
    html = fp.read()
soup = BeautifulSoup(html)
terms = pd.DataFrame(columns=['ConceptTerm', 'Def'])
for tag in soup.findAll('dd'):
    heading = []
    for child in tag.children:
        heading.append(child.string)
    row_data = [tag.find_previous_sibling('dt').text, heading[0]]
    terms.loc[len(terms.index)] = row_data
terms = terms.replace(r':', '', regex=True)
terms['LearningStatement'] = terms['ConceptTerm'] + "  " + terms['Def']

graph = Graph("http://neo4j:redsquare@localhost:7474")
terms = terms.drop_duplicates(subset=['ConceptTerm'], keep = 'first')
terms.reset_index(drop=True, inplace=True)
statements = pd.DataFrame(columns=['ConceptTerm_extracted', 'LearningStatement'])
for term in terms.ConceptTerm:
    try:
        pulled_statements = pd.DataFrame(graph.data("""MATCH (g) WHERE toLower(g.term) = toLower('""" + term + """') OPTIONAL MATCH path=(g)-[*1..3]-(h:LearningStatement) RETURN DISTINCT h.statement"""))
        for p_s in pulled_statements['h.statement']:
            statement = [term, p_s]
            if statement[1] == None:
                pass
            else:
                statements.loc[len(statements.index)] = statement
#        print p_s
    except:
        pass

terms.dropna(axis=0, inplace=True)
terms.reset_index(drop=True, inplace=True)

suggest_df = pd.DataFrame(columns=['ConceptTerm', 'LearningStatement_1','LearningStatement_2', 'SimilarityIndex', 'SimilarityCount', 'Suggest1', 'Suggest2' ])
gap_df = pd.DataFrame(columns=['LearningStatement_2'])                 
for r in range(len(terms)):   
    sample1 = pd.DataFrame({'LearningStatement': list(statements.loc[statements['ConceptTerm_extracted'] == terms.iloc[r].ConceptTerm].LearningStatement)})
    print "Compiling samples"

    if sample1.empty:                                                             
        sample1 = file_io.read_xlsx('../data/machine_assistance/%s_test.xlsx' % subject)
        tfidf = pickle.load(open('../data/machine_assistance/%s_concept_term_vocabulary_full_matrix.pickle' % subject, "rb" ))                                               
    else:
        tfidf = tf_idf.tf_idf_fit(sample1.LearningStatement, '../data/machine_assistance/%s_concept_term_vocabulary.json' % subject)                                    
    sample2 = pd.DataFrame({'LearningStatement': [terms.iloc[r].LearningStatement]})
    row_data, gap_data = similarity.suggest(.1, sample1, sample2, tfidf, subject, False)   

    row_data['ConceptTerm'] = terms.ConceptTerm[r]
    suggest_df = suggest_df.append(row_data) 
    gap_df = gap_df.append(gap_data)  
    print suggest_df

lemmatizer = nltk.stem.WordNetLemmatizer()

for i in range(len(suggest_df)):
    result = re.sub(" [\(\[].*?[\)\]]", "", suggest_df.iloc[i].ConceptTerm)
    suggest_df.iloc[i, suggest_df.columns.get_loc('ConceptTerm')] = result
    result = re.sub(" [\(\[].*?[\)\]]", "", suggest_df.iloc[i].LearningStatement_2)
    suggest_df.iloc[i, suggest_df.columns.get_loc('LearningStatement_2')] = result
    tokens1 = nltk.pos_tag(nltk.tokenize.word_tokenize(suggest_df.iloc[i].LearningStatement_2))
    tokens2 = nltk.pos_tag(nltk.tokenize.word_tokenize(suggest_df.iloc[i].ConceptTerm))
    a = []
    for t in range(len(tokens1)):
        if "V" in tokens1[int(t)][1]:
            token = lemmatizer.lemmatize(tokens1[int(t)][0], 'v')
        else:
            token = lemmatizer.lemmatize(tokens1[int(t)][0])
        a.append(token.lower())
    a1 = ' '.join(a)
    b = []
    for t in range(len(tokens2)):
        token = lemmatizer.lemmatize(tokens2[int(t)][0])
        b.append(token.lower())
    b1 = ' '.join(b) + ' be'
    suggest_df.iloc[i, suggest_df.columns.get_loc('Suggest2')] = b1 in a1
    suggest_df.iloc[i, suggest_df.columns.get_loc('Suggest1')] = all(i in a for i in b)

suggest_df.sort_values('SimilarityIndex', ascending=False)
TT8 = suggest_df[(suggest_df['Suggest1'] == True) & (suggest_df['Suggest2'] == True) & (suggest_df['SimilarityIndex'] > .8)]
TF8 = suggest_df[(suggest_df['Suggest1'] == True) & (suggest_df['Suggest2'] == False) & (suggest_df['SimilarityIndex'] > .8)]
FF8 = suggest_df[(suggest_df['Suggest1'] == False) & (suggest_df['Suggest2'] == False) & (suggest_df['SimilarityIndex'] > .8)]
TT7 = suggest_df[(suggest_df['Suggest1'] == True) & (suggest_df['Suggest2'] == True) & (suggest_df['SimilarityIndex'] <= .8)]
TF5 = suggest_df[(suggest_df['Suggest1'] == True) & (suggest_df['Suggest2'] == False) & (suggest_df['SimilarityIndex'] > .5)]
single_suggest_df = pd.concat([TT8, TF8, FF8, TT7, TF5])
single_suggest_df = single_suggest_df.drop_duplicates(subset=['ConceptTerm'], keep = 'first')

common = suggest_df.merge(single_suggest_df,on=['ConceptTerm'])
unmatched_df = suggest_df[(~suggest_df.ConceptTerm.isin(common.ConceptTerm))]

file_io.write_xlsx(single_suggest_df, sys.argv[2], sheet = 'Suggest')
file_io.write_xlsx(unmatched_df, sys.argv[2], sheet = 'Unmatched') 
file_io.write_xlsx(gap_df, sys.argv[2], sheet = 'Gap Analysis') 


import sys; sys.path.insert(0, "..")                                   
import utils.file_io as file_io       
import os
import sys
import urllib
import pandas as pd

def bt_nt(sample = '../data/dbpedia/graph_db/graph_test.xlsx'):
    base_url = 'http://downloads.dbpedia.org/current/core-i18n/en/'
    relation = '../data/dbpedia/skos_categories_en.tql.bz2'
    if not os.path.isfile(relation):
        urllib.urlretrieve(os.path.join(base_url, os.path.basename(relation)), relation) 
    
    broader= pd.read_csv(relation, compression = "bz2", sep= " ", skiprows = [0,1], header = None, names = ["ConceptTerm", "relation", "term", "Old", "."])
    broader.replace({'<http:\/\/dbpedia.org\/resource\/Category:': ''}, regex = True, inplace = True)
    broader.replace({'<http:\/\/www.w3.org\/2004\/02\/skos\/core#': ''}, regex = True, inplace = True)
    broader.replace({'_': ' '}, regex = True, inplace = True)  
    broader.replace({'>': ''}, regex = True, inplace = True)
    broader.replace({'@en': ''}, regex = True, inplace = True)

    concept_terms = file_io.read_xlsx(sample)  

    mask_broad = broader['relation'].isin(['broader'])
    broader_terms = broader[mask_broad] 
    narrow_broad = concept_terms.merge(broader_terms[['ConceptTerm', 'term']], how = 'inner')
    narrow_broad.columns = ['ConceptTerm', 'ConceptTermDBID', 'BroadTerm']

    # This is a really hacky way to find narrow -> broad relationships, but it saves having to load
    # the big dataset into memory more than once. New ideas are welcome!
    broader.columns = ['term', 'relation', 'ConceptTerm', 'Old', '.']
    mask_narrow = broader['relation'].isin(['broader'])
    narrower_terms = broader[mask_narrow] 
    broad_narrow = concept_terms.merge(narrower_terms[['ConceptTerm', 'term']], how = 'inner')
    broad_narrow.columns = ['ConceptTerm', 'ConceptTermDBID', 'NarrowTerm']

    return narrow_broad, broad_narrow

def main():
    narrow_broad, broad_narrow = bt_nt(sys.argv[1])
    file_io.write_xlsx(narrow_broad, file='../data/dbpedia/graph_db/narrow_broad.xlsx') 
    file_io.write_xlsx(broad_narrow, file='../data/dbpedia/graph_db/broad_narrow.xlsx') 


if __name__ == "__main__":
    main()


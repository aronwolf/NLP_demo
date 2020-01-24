import sys; sys.path.insert(0, "..")                                    
import utils.file_io as file_io 
import os
import sys
import urllib
import pandas as pd

def npt(sample = '../data/dbpedia/graph_db/graph_test.xlsx'):
    base_url = 'http://downloads.dbpedia.org/current/core-i18n/en/'
    redirects = '../data/dbpedia/redirects_en.tql.bz2'
    if not os.path.isfile(redirects):
        urllib.urlretrieve(os.path.join(base_url, os.path.basename(redirects)), redirects) 
    
    redirect_sheet = pd.read_csv(redirects, compression = "bz2", sep= " ", skiprows = 0, header = None, names = ["NPT", "Type", "PT", "Old", "."])
    redirect_sheet.replace({'<http:\/\/dbpedia.org\/resource\/': ''}, regex = True, inplace = True)
    redirect_sheet.replace({'_': ' '}, regex = True, inplace = True) 
    redirect_sheet.replace({'>': ''}, regex = True, inplace = True)   

    concept_terms = file_io.read_xlsx(sample) 

    pts = list(redirect_sheet.PT) 

    df1 = pd.DataFrame({'ConceptTerm': list(pts)})

    df_pt = pd.concat([redirect_sheet, df1], axis = 1)

    nonprefered = concept_terms.merge(df_pt[['ConceptTerm', 'NPT']], how = 'inner') 

    return nonprefered

def main():
    npt_df = npt(sys.argv[1])
    file_io.write_xlsx(npt_df, file= '../data/dbpedia/graph_db/nonprefered.xlsx')

if __name__ == "__main__":
    main()


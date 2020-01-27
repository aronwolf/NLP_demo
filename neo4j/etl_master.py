from __future__ import unicode_literals   
import sys; sys.path.insert(0, "..")                                   
import sys; sys.path.insert(0, "../dbpedia/")    
import utils.file_io as file_io
import dbpedia_redirects
import dbpedia_skos       
import sys
import pandas as pd
import re

def etl(sample):
    concept_terms = file_io.read_xlsx(sample)    
    npt = dbpedia_redirects.npt(sample)
    narrow_broad, broad_narrow = dbpedia_skos.bt_nt(sample)

    series1 = npt['NPT']                                         
    series2 = broad_narrow['NarrowTerm']
    series3 = narrow_broad['BroadTerm']                                                       
    series_combined = pd.concat([series1, series2, series3], axis = 0)

    scrubber = re.compile(r'[\u0250-\uffff]+')
    scrubbed_list = []                                                                       
    for i in series_combined:
        result = scrubber.sub('', i.decode("utf-8"))
        scrubbed_list.append(result)
    df_combined = pd.DataFrame({'ConceptTerm':scrubbed_list})
    df_combined = df_combined[~df_combined['ConceptTerm'].isin([''])]

    df_all = df_combined.merge(concept_terms[['ConceptTerm', 'ConceptTermDBID']], how = "outer") 
    df_all_dedupe = df_all.drop_duplicates(keep = 'first')

    df_new_terms = pd.DataFrame(df_all_dedupe.loc[df_all_dedupe.ConceptTermDBID.isnull(), 'ConceptTerm']) 

    df_new_terms = df_new_terms.reset_index() 
    df_new_terms['Normalized'] = 'Unnormalized'
    df_new_terms.columns = ['ConceptTermDBID', 'ConceptTerm', 'Normalized']  
    df_new_terms['ConceptTermDBID'] = df_new_terms.index + df_all_dedupe['ConceptTermDBID'].max() + 1

    concept_terms['Normalized'] = 'Normalized'

    df_old_and_new_terms = pd.concat([concept_terms, df_new_terms], axis = 0)
    df_old_and_new_terms['labels'] = df_old_and_new_terms['Normalized'] + ";ConceptTerm"
    df_final_old_and_new_terms = df_old_and_new_terms[['ConceptTermDBID', 'ConceptTerm', 'labels']]
    df_final_old_and_new_terms[list(['ConceptTermDBID'])] = df_final_old_and_new_terms[list(['ConceptTermDBID'])].astype(int)
    df_final_old_and_new_terms.replace({'\n': ''}, regex = True, inplace = True)


    df_broad_ids = narrow_broad.merge(df_final_old_and_new_terms, left_on = 'BroadTerm', right_on = 'ConceptTerm', how = "inner")
    df_final_broad_ids = df_broad_ids[['ConceptTermDBID_x', 'ConceptTermDBID_y']]
    df_final_broad_ids['NarrowTermID'] = 'CT' + df_final_broad_ids['ConceptTermDBID_x'].astype(str)
    df_final_broad_ids['BroadTermID'] = 'CT' + df_final_broad_ids['ConceptTermDBID_y'].astype(str)
    df_narrow_ids = broad_narrow.merge(df_final_old_and_new_terms, left_on = 'NarrowTerm', right_on = 'ConceptTerm', how = "inner")
    df_final_narrow_ids = df_narrow_ids[['ConceptTermDBID_x', 'ConceptTermDBID_y']]
    df_final_narrow_ids['BroadTermID'] = 'CT' + df_final_narrow_ids['ConceptTermDBID_x'].astype(str)
    df_final_narrow_ids['NarrowTermID'] = 'CT' + df_final_narrow_ids['ConceptTermDBID_y'].astype(str)
    df_final_hierarchical_terms = pd.concat([df_final_broad_ids, df_final_narrow_ids], axis = 0)
    df_final_hierarchical_terms_dedupe = df_final_hierarchical_terms.drop_duplicates(subset = ['ConceptTermDBID_x', 'ConceptTermDBID_y'], keep = 'first') 
    df_final_hierarchical_terms_dedupe.to_csv('../data/dbpedia/graph_db/graph_load_hierarchical.csv', index = False, encoding='utf-8')

    df_npt_ids = npt.merge(df_final_old_and_new_terms, left_on = 'NPT', right_on = 'ConceptTerm', how = "inner")
    df_final_npt_ids = df_npt_ids[['ConceptTermDBID_x', 'ConceptTermDBID_y']]
    df_final_npt_ids['PreferredTermID'] = 'CT' + df_final_npt_ids['ConceptTermDBID_x'].astype(str)
    df_final_npt_ids['NPTID'] = 'CT' + df_final_npt_ids['ConceptTermDBID_y'].astype(str)
    df_final_npt_ids.to_csv('../data/dbpedia/graph_db/graph_load_npt.csv', index = False, encoding='utf-8')

#    spreadsheet = file_io.read_xlsx('../data/machine_assistance/bento.xlsx')
    spreadsheet = file_io.read_xlsx('../data/machine_assistance/business_test.xlsx')

    df_concept_chain = spreadsheet[['ConceptChain', 'ConceptChainDBID', 'ConceptTermDBID']]
    mask_chain = df_concept_chain.ConceptChain.str.contains('\+')
    df_chains = df_concept_chain[mask_chain]
    df_chain1 = df_chains[['ConceptTermDBID', 'ConceptChainDBID']]
    df_chain2 = df_chains[['ConceptChainDBID', 'ConceptTermDBID']]
    df_chains_all = df_chain1.merge(df_chain2, left_on = 'ConceptChainDBID', right_on = 'ConceptChainDBID', how = 'outer')
    df_chains_all_dedupe = df_chains_all[['ConceptTermDBID_x', 'ConceptTermDBID_y']]
    df_chains_all_dedupe = df_chains_all_dedupe.drop_duplicates(keep = 'first')
    df_final_chains = df_chains_all_dedupe.loc[~(df_chains_all_dedupe['ConceptTermDBID_x'] == df_chains_all_dedupe['ConceptTermDBID_y'])]
    df_final_chains['RelatedTermID_x'] = 'CT' + df_final_chains['ConceptTermDBID_x'].astype(str)
    df_final_chains['RelatedTermID_y'] = 'CT' + df_final_chains['ConceptTermDBID_y'].astype(str)
    df_final_chains.to_csv('../data/dbpedia/graph_db/graph_load_concept_chains.csv', index = False, encoding='utf-8')


    df_final_subject = df_final_old_and_new_terms.merge(spreadsheet[['ConceptTermDBID', 'Subject']], left_on = 'ConceptTermDBID', right_on = 'ConceptTermDBID', how = 'left')
    df_final_subject[':LABEL'] = df_final_subject['labels'].astype(str) + ';' + df_final_subject['Subject'].astype(str)
    df_final_subject.replace({';nan': ''}, regex = True, inplace = True)
    df_final_subject['id'] = 'CT' + df_final_subject['ConceptTermDBID'].astype(str)
    df_final_terms = df_final_subject[['id', 'ConceptTerm', ':LABEL']]
    df_final_terms.columns = ['ConceptTermDBID', 'term', ':LABEL']
#    df_final_terms_deduped = df_final_terms.drop_duplicates(keep = 'first')
    df_final_terms_deduped = df_final_terms.drop_duplicates(subset=['ConceptTermDBID'], keep='first')
    df_final_terms_deduped.replace({'\s+': ' '}, regex = True, inplace = True)
    mask = (df_final_terms_deduped['term'] != ' ')
    df_final_terms_scrubbed = df_final_terms_deduped[mask]
    df_final_terms_scrubbed.to_csv('../data/dbpedia/graph_db/graph_load_concept_term_ids.csv', index = False, encoding='utf-8')
    
    df_statements = spreadsheet[['LearningStatementDBID', 'LearningStatement']]
    df_statements_type_sheet = file_io.read_xlsx('../data/dbpedia/graph_db/All_LS_Bento_08312017.xlsx')
    df_statements_type = df_statements_type_sheet[['id', 'type', 'structure']]
    df_statements_type_ids = df_statements.merge(df_statements_type.dropna(axis = 0, how = 'any'), left_on='LearningStatementDBID', right_on='id', how='outer') 
    df_statements_type_ids = df_statements_type_ids.fillna('')  
    df_final_statements = df_statements_type_ids[['LearningStatementDBID', 'LearningStatement']]
#    df_statements_type_ids [list(['structure'])] = df_statements_type_ids[list(['structure'])].astype(int)
    df_final_statements[':LABEL'] = "LearningStatement;" + df_statements_type_ids['type'] + " " + df_statements_type_ids['structure'].astype(str)
    df_final_statements_deduped = df_final_statements.drop_duplicates(subset=['LearningStatementDBID'], keep = 'first')
    df_final_statements_deduped['LearningStatementDBID'] = 'LS' + df_final_statements_deduped['LearningStatementDBID'].astype(str) 
#    df_final_statements_deduped.columns = ['id', 'statement', ':LABEL', 'LearningStatementDBID']
    df_final_statements_deduped.to_csv('../data/dbpedia/graph_db/graph_load_learning_statement_ids.csv', index = False, encoding='utf-8')

    df_ct_ls = spreadsheet[['ConceptTermDBID', 'LearningStatementDBID']]
    df_ct_ls['term'] = 'CT' + df_ct_ls['ConceptTermDBID'].astype(str)
    df_ct_ls['statement'] = 'LS' + df_ct_ls['LearningStatementDBID'].astype(str)
    df_final_ct_ls = df_ct_ls[['term', 'statement']]
    df_final_ct_ls.columns = ['ConceptTermDBID', 'LearningStatementDBID']
    df_final_ct_ls.to_csv('../data/dbpedia/graph_db/graph_load_CT_LS.csv', index = False, encoding='utf-8')

def main():
    etl(sys.argv[1])

if __name__ == "__main__":
    main()


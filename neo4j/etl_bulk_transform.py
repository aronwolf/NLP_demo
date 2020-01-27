import sys; sys.path.insert(0, "..") 
import etl_master as etl_master
import pandas as pd
import os

def etl_transform(sample):
    etl_master.etl(sample)

    npt = pd.read_csv('../data/dbpedia/graph_db/graph_load_npt.csv')
    npt_clean = npt[['PreferredTermID', 'NPTID']]
    npt_clean.columns = [':START_ID', ':END_ID']
    npt_clean.to_csv('../data/dbpedia/graph_db/graph_load_npt.csv', index = False, encoding='utf-8')
    npt_clean.columns = [':END_ID', ':START_ID']
    npt_clean.to_csv('../data/dbpedia/graph_db/graph_load_pt.csv', index = False, encoding='utf-8')

    bt_nt = pd.read_csv('../data/dbpedia/graph_db/graph_load_hierarchical.csv')  
    bt_nt_clean = bt_nt[['BroadTermID', 'NarrowTermID']]  
    bt_nt_clean.columns = [':START_ID', ':END_ID']
    bt_nt_clean.to_csv('../data/dbpedia/graph_db/graph_load_broad_narrow.csv', index = False, encoding='utf-8')     
    bt_nt_clean.columns = [':END_ID', ':START_ID']

    bt_nt_clean.to_csv('../data/dbpedia/graph_db/graph_load_narrow_broad.csv', index = False, encoding='utf-8')
    os.remove('../data/dbpedia/graph_db/graph_load_hierarchical.csv')

    ct_ls = pd.read_csv('../data/dbpedia/graph_db/graph_load_CT_LS.csv') 
    ct_ls.columns = [':START_ID', ':END_ID']            
    ct_ls.to_csv('../data/dbpedia/graph_db/graph_load_CT_LS.csv', index = False, encoding='utf-8')
    ct_ls.columns = [':END_ID', ':START_ID']                         
    ct_ls.to_csv('../data/dbpedia/graph_db/graph_load_LS_CT.csv', index = False, encoding='utf-8')

    cc = pd.read_csv('../data/dbpedia/graph_db/graph_load_concept_chains.csv')
    cc_clean = cc[['RelatedTermID_x', 'RelatedTermID_y']]                  
    cc_clean.columns = [':START_ID', ':END_ID']
    cc_clean.to_csv('../data/dbpedia/graph_db/graph_load_concept_chains.csv', index = False, encoding='utf-8')                                                             

    term = pd.read_csv('../data/dbpedia/graph_db/graph_load_concept_term_ids.csv')
    term.columns = [':ID', 'term', ':LABEL']
    term.to_csv('../data/dbpedia/graph_db/graph_load_concept_term_ids.csv', index = False, encoding='utf-8') 

    statement = pd.read_csv('../data/dbpedia/graph_db/graph_load_learning_statement_ids.csv')
    statement.columns = [':ID', 'statement', ':LABEL']
    statement.to_csv('../data/dbpedia/graph_db/graph_load_learning_statement_ids.csv', index = False, encoding='utf-8')

def main():
    etl_transform(sys.argv[1])

if __name__ == "__main__":
    main()

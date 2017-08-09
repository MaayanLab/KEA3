import pandas as pd
import numpy as np

<<<<<<< HEAD
#Create engine for localhost
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:systemsbiology@localhost:3306/test')

#Read in species dataframe for use in program
species_dataframe = pd.read_sql_query('SELECT * FROM species', engine)
species_dataframe.head()

def GMT_to_SIG(gmt):
    with open(gmt, 'r') as openfile:
        gmt_data = [x.strip().split('\t') for x in openfile.readlines()]
        
=======
def GMT_to_SIG(gmt_data, filename):
     
>>>>>>> working
    gmt_dict = {x[0]: x[2:] for x in gmt_data}
                
    sig = pd.DataFrame([[x[0], y] for x in gmt_data for y in x[2:]])

    #Insert first four columns for .sig file format (NaNs)
    sig.insert(1, 'NA-1', str(np.nan))
    sig.insert(2, 'NA-2', str(np.nan))
    sig.insert(3, 'NA-3', str(np.nan))
    sig.insert(4, 'NA-4', str(np.nan))
                
    #Insert first four columns for .sig file format (NaNs)
    sig.insert(6, 'NA-5', str(np.nan))
    sig.insert(7, 'NA-6', str(np.nan))
    sig.insert(8, 'NA-7', str(np.nan))
    sig.insert(9, 'NA-8', str(np.nan))
<<<<<<< HEAD
                
=======

>>>>>>> working
    #Insert column corresponding to sign 
    sig.insert(10, 'Sign', str(np.nan))
                
    #Insert column specifying interaction type as unknown
    sig.insert(11, 'Interaction', str(np.nan))

    #Insert column specifying interaction type as unknown
    sig.insert(12, 'PubMed', str(np.nan))

    #Create dictionary 'sigd' with index numbers as keys
    sigd = dict([(key, '') for key in sig.index])

    # loop through rows with iterrows()
    for index, rowData in sig.iterrows():
        line = ('\t'.join(rowData))
        sigd[index] = line

<<<<<<< HEAD
    gmt_name = gmt.split(".", 2)[0]
=======
    gmt_name = filename.split(".", 2)[0]
>>>>>>> working

    #Transfer tab-separated info into a new txt file
    #Make sure to include in ReadMe corresponding column names
    with open('%s.sig' %gmt_name, 'w') as openfile:
        for index in sigd:
            openfile.write(str(sigd[index]) + '\n')

    sig = pd.read_table("%s.sig" %gmt_name, header = None)

    return sig

<<<<<<< HEAD
def SIG_to_Genes(sig, submission_fk, organism):
    
=======
def SIG_to_Genes(sig, submission_fk, organism, engine):

    if len(sig.columns) != 13:
        return "Error"

    #Read in species dataframe for use in program
    species_dataframe = pd.read_sql_query('SELECT * FROM species', engine)
    species_dataframe.head()

>>>>>>> working
    sig = pd.DataFrame(sig)
    
    #Add species_fk to all of the interactions
    interaction_dataframe = sig[[0, 5]]
    
<<<<<<< HEAD
    if '_' in interaction_dataframe[0].iloc[0]:
=======
    #Must obtain Organism of the individual kinases (if none available, use organism submitted by users)
    if interaction_dataframe[0].str.contains('_').all():
>>>>>>> working
        interaction_dataframe['species'] = [x.split('_')[-1] for x in interaction_dataframe[0]]

        for index, species in interaction_dataframe.species.iteritems():
            if species in ['HUMAN', 'human', 'Human']:
                interaction_dataframe.species[index] = 'Homo sapiens'
            if species in ['MOUSE', 'mouse', 'Mouse']:
                interaction_dataframe.species[index] = 'Mus musculus'
<<<<<<< HEAD
=======
            else:
                interaction_dataframe.species[index] = '%s' %organism

    if interaction_dataframe[0].str.contains('-').all():
        interaction_dataframe['species'] = [x.split('-')[-1] for x in interaction_dataframe[0]]

        for index, species in interaction_dataframe.species.iteritems():
            if species in ['HUMAN', 'human', 'Human']:
                interaction_dataframe.species[index] = 'Homo sapiens'
            if species in ['MOUSE', 'mouse', 'Mouse']:
                interaction_dataframe.species[index] = 'Mus musculus' 
            else:
                interaction_dataframe.species[index] = '%s' %organism      
>>>>>>> working
    else:
        interaction_dataframe['species'] = '%s' %organism
        print(organism)
    
    pairs = interaction_dataframe.merge(species_dataframe, left_on='species', right_on='species_name', how='left')
<<<<<<< HEAD
    pairs.drop('species', axis = 1, inplace = True)
    pairs.drop('species_name', axis =1, inplace = True)
    pairs.columns = ['source', 'target', 'species_id']
    
    #View Dataframe
    #No need to drop duplicates (no duplicates in this dataframe)
    #Remove indication of species from name of the source
    pairs['source'] = [x.split('_')[:-1] for x in interaction_dataframe[0]]
    pairs['source'] = ['_'.join(x) for x in pairs['source']]
    
    # Need to lowercase and title names of mouse kinases to later
    #prevent id-ing of these kinases to the human equivalent
    for index,rowData in pairs.iterrows():
        if rowData.species_id == 2:
            pairs.source[index] = rowData.source.lower()
            pairs.target[index] = rowData.target.lower()
        if rowData.species_id == 1:
            pairs.source[index] = rowData.source.upper()
            pairs.target[index] = rowData.target.upper()
=======

    #Remove indication of species from name of the source and drop unnecessary columns if needed
    if interaction_dataframe[0].str.contains('_').all():
        pairs['source'] = [x.split('_')[:-1] for x in interaction_dataframe[0]]
        pairs['source'] = ['_'.join(x) for x in pairs['source']]
        pairs.drop(0, axis=1, inplace=True)
        pairs.drop('species', axis = 1, inplace = True)
        pairs.drop('species_name', axis =1, inplace = True)
        pairs.columns = ['target', 'species_id', 'source']
    else:
        pairs.drop('species', axis = 1, inplace = True)
        pairs.drop('species_name', axis =1, inplace = True)
        pairs.columns = ['source', 'target', 'species_id']
    

    #No need to drop duplicates (no duplicates in this dataframe)
    
    # Need to uppercase all names in the dataframe to standardize names
    # across different files

    pairs['source'] = [name.upper() for name in pairs.source]
    pairs['target'] = [name.upper() for name in pairs.target]

>>>>>>> working
    pairs.drop_duplicates(inplace=True)
    
    #Create separate dataframes for the source and target genes
    source_genes = pd.DataFrame(dict(gene_symbol = pairs.source, species_fk = pairs.species_id))
    source_genes.drop_duplicates(inplace=True)
    source_genes.reset_index(inplace=True, drop=True)
    target_genes = pd.DataFrame(dict(gene_symbol = pairs.target, species_fk = pairs.species_id))
    target_genes.drop_duplicates(inplace = True)
    target_genes.reset_index(inplace=True, drop=True)
    
    #Concat these genes into a single dataframe
    genes = pd.concat([source_genes, target_genes])
    genes.drop_duplicates(inplace=True)
    
    #Use INSERT_IGNORE to add these genes and targets to the dataframe
    insert_ignore = "INSERT IGNORE INTO genes (gene_symbol, species_fk) VALUES" + ', '.join(['("{gene_symbol}", {species_fk})'.format(**rowData) for index, rowData in genes.iterrows()])
    # Create or add new entries to the genes table using 'insert-ignore' functionality
    engine.execute(insert_ignore)
    genes_df = pd.read_sql_query('SELECT * FROM genes', engine)
    
    #Use genes table to isolate fk of these source and target genes
    #fk will later be used when creating the interaction database
<<<<<<< HEAD
    source_fk = pairs.merge(genes_df, left_on='source', right_on='gene_symbol', how='left')
    source_fk.drop_duplicates(['source', 'target', 'species_id'], inplace = True)
    source_fk.drop(['source', 'target', 'species_id', 'species_fk',
                           'gene_symbol', 'description'], axis=1, inplace=True)
    target_fk = pairs.merge(genes_df, left_on='target', right_on='gene_symbol', how='left')
    target_fk.drop_duplicates(['source','target'], inplace = True)
    target_fk.drop(['source', 'target', 'species_id', 
                           'gene_symbol', 'species_fk', 'description'], axis=1, inplace=True)
    
    interactions=pd.concat([source_fk, target_fk], axis = 1)
    
    interactions.insert(2, 'submission_fk', submission_fk)
    interactions.columns = ['source_gene_fk', 'target_gene_fk', 'submission_fk']
    return interactions
=======
    source_fk = pairs.merge(genes_df, how='left', left_on=['source', 'species_id'], 
                          right_on=['gene_symbol', 'species_fk'])
    source_fk.drop_duplicates(['source', 'target', 'species_id'], inplace = True)
    source_fk.drop(['source', 'target', 'species_id', 'species_fk',
                           'gene_symbol', 'description'], axis=1, inplace=True)
    target_fk = pairs.merge(genes_df, how='left', left_on=['target', 'species_id'], 
                        right_on=['gene_symbol', 'species_fk'])
    target_fk.drop_duplicates(['source', 'target', 'species_id'], inplace = True)
    target_fk.drop(['source', 'target', 'species_id', 
                           'gene_symbol', 'species_fk', 'description'], axis=1, inplace=True)

    #Create and format dataframe 'interactions' corresponding to all interactions in this SIG file
    interactions=pd.concat([source_fk, target_fk], axis = 1)
    interactions.insert(2, 'submission_fk', submission_fk)
    interactions.columns = ['source_gene_fk', 'target_gene_fk', 'submission_fk']
    return interactions
>>>>>>> working

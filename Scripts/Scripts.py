# Import libraries
import urllib, urllib.request, urllib.parse
from io import StringIO
import pandas as pd

########################################################################
####### Scripts ########################################################
########################################################################

###############
# 1. Function to convert Uniprot ID to Gene Symbols
###############

# Define to get UniProt ID to gene name conversion
def uniprot_to_symbol(uniprot_id_list):
    
    # Get URL of UniProt
    url = 'http://www.uniprot.org/uploadlists/'
    
    # Set parameters of search
    params = {
        'from':'ACC',
        'to':'GENENAME',
        'format':'tab',
        'query':' '.join(uniprot_id_list)
    }
    
    # Set request
    request = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode("utf-8"))
    
    # Get response
    response = urllib.request.urlopen(request)
    
    # Read response
    results = response.read().decode('utf-8')
    
    # Convert to dataframe
    id_mapping_dataframe = pd.read_csv(StringIO(results), sep='\t')
    
    # Convert to dictionary
    id_mapping_dict = id_mapping_dataframe.set_index('From').to_dict()['To']
    
    # Convert symbols.  If symbol is not available, returns None
    gene_symbol_list = [id_mapping_dict[uniprot_id] if uniprot_id in id_mapping_dict.keys() else None for uniprot_id in uniprot_id_list]
    
    return gene_symbol_list
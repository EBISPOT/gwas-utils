from solrWrapper import solr_wrapper


def removeUpdatedSolrData(solr_object, updated_pmids):

    # Removing all all trait documents:
    remove_trait_docs(solr_object)

    # Remove retracted publications:
    if len(updated_pmids['removed']): 
        print("[Info] Deleting retracted publications from solr: {}".format(updated_pmids['removed']))
        remove_query = generate_query(updated_pmids['removed'])
        solr_object.delete_query(remove_query)

    # Remove updated publications:
    if len(updated_pmids['updated']): 
        print("[Info] Deleting updated publications from solr: {}".format(updated_pmids['updated']))
        remove_query = generate_query(updated_pmids['updated'])
        solr_object.delete_query(remove_query)

    return 0



def generate_query(pmid_list = None):

    if pmid_list:
        # Build remove query:
        pmid_query_list = ' OR '.join(['pubmedId:{}'.format(pmid) for pmid in pmid_list])
        remove_query = '(resourcename:study OR resourcename:association) AND ( {} )'.format(pmid_query_list)

    else:
        remove_query = ''
        
    return remove_query


# Removing all efo and disease trait documents:
def remove_trait_docs(solr_object):
    '''
    Simple query to remve all trait documents.
    '''
    
    solr_object.delete_query("resourcename:efotrait") # removing EFO trait documents
    solr_object.delete_query("resourcename:diseasetrait") # removing disease trait documents
    
    return 0

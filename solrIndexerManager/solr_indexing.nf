params.newInstance = ''
params.oldInstance = ''
params.solrHost = ''
params.solrCore = ''
params.solrPort = ''
params.wrapperScript = ''
params.fullIndex = 'True'

// ------------------------------------------------------------- //
// Determine updates from databases and update Solr              //
// ------------------------------------------------------------- //

process get_updates {

  memory { 1.GB * task.attempt }
  time { 1.hour * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus in 2..140 ? 'retry' : 'terminate' }

  output:
  stdout into db_updates

  """
  #!/usr/bin/env python

  from solrIndexerManager.components import getUpdated
  from solrWrapper import solr_wrapper
  from solrIndexerManager.components import solrUpdater

  # Get updates
  new_table = getUpdated.get_studies("$params.newInstance")
  if $params.fullIndex:
      db_updates = {
          "added": new_table.PUBMED_ID.unique().tolist(),  # As if all publications in the new table was newly added
          "removed": ['*'],  # As if all publications were removed.
          "updated": []
      }
  else:
      old_table = getUpdated.get_studies("$params.oldInstance")
      db_updates = getUpdated.get_db_updates(old_table, new_table)

  # Removed associations and studies for all updated/deleted studies + removing all trait documents:
  solr_object = solr_wrapper.solrWrapper(host="$params.solrHost", port="$params.solrPort", core="$params.solrCore", verbose=True)
  solrUpdater.removeUpdatedSolrData(solr_object, db_updates)

  print(db_updates)
  """
}






db_updates.view { it }




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
  file 'db_updates.json' into db_updates

  """
  #!/usr/bin/env python

  import json
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

  with open('db_updates.json', 'w') as f:
      json.dump(db_updates, f)
  """
}


// ------------------------------------------------------------- //
// Run the solr indexer                                          //
// ------------------------------------------------------------- //

process solr_indexer {

  memory { 2.GB * task.attempt }
  time { 4.hour * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus in 2..140 ? 'retry' : 'terminate' }

  input:
  file db_updates_file from db_updates

  output:
  stdout into ch

  """
  #!/usr/bin/env python

  import json


  db_updates = None
  with open("${db_updates_file}") as f:
      db_updates = json.load(f)

  def job_generator(db_updates, wrapper):
      # Indexing jobs with associations and studies for each pubmed ID:
      jobs = {pmid : '{} -d -e -p {}'.format(wrapper, pmid) for x in db_updates.values() for pmid in x if pmid != '*'}
      # Indexing job to generate disease trait and efo trait documents:
      jobs['efo_traits'] = '{} -a -s -d '.format(wrapper)
      jobs['disease_traits'] = '{} -a -s -e '.format(wrapper)
      return jobs

  joblist = job_generator(db_updates, "$params.wrapperScript")
  print(joblist)
  """
}




ch.view { it }




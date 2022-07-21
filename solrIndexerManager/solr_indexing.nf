nextflow.enable.dsl=2

params.job_map_file = ''
params.log_path = ''

// ------------------------------------------------------------- //
// Run the solr indexer jobs                                     //
// ------------------------------------------------------------- //


process run_solr_indexer {
  tag "$id"
  memory { 4.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus in 2..140 ? 'retry' : 'terminate' }

  input:
  tuple val(id), val(cmd)

  output:
  stdout

  """
  echo $id
  $cmd
  """
}


workflow {
  jobs = channel.fromPath("$params.job_map_file").splitCsv()
  run_solr_indexer(jobs)
}

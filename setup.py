from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    description='A variety of utilities for activities involved in the running of the GWAS Catalog',
    name='gwasUtils',
    version='0.1-SNAPSHOT',
    packages=['dataExport','dataReleaseQC','dataReleaseQC.functions','epmcXMLTools','solrIndexerManager','solrIndexerManager.components','solrWrapper', 'ftpSummaryStatsScript', 'harmonisationUtils'],
    entry_points={
        "console_scripts": ['unpublish-study-export = dataExport.unpublish_study_export:main',
                            'test-pruning = dataReleaseQC.test_pruning:main',
                            'test-missing-data = dataReleaseQC.test_missing_data:main',
                            'test-solr-data = dataReleaseQC.test_solr_data:main',
                            'extract-epmc-tables = epmcXMLTools.extract_epmc_tables:main',
                            'indexer-manager = solrIndexerManager.indexer_manager:main',
                            'stats-file-generator = dataReleaseQC.stats_file_generator:main',
                            'data-release-report = dataReleaseQC.data_release_report:main',
                            'ftp-sync = ftpSummaryStatsScript.ftp_sync:main',
                            'depo-sumstats-sync = ftpSummaryStatsScript.depo_ftp_to_staging:main',
                            'queue-harmonisation = harmonisationUtils.move_eligible_files_to_harmonisation:main'
                            ]
    },
    license='',
    install_requires=requirements
)
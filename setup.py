from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    description='A variety of utilities for activities involved in the running of the GWAS Catalog',
    name='gwasUtils',
    version='0.1.27b.9',
    data_files=[('r_scripts',['catalogPlots/dataReleaseTimer.R', 'catalogPlots/SumStats_plotter.R', 'catalogPlots/TA_vs_GWAS_publication.R']),
                ('nf', ['solrIndexerManager/solr_indexing.nf'])],
    packages=['gwasAssociationFilter',
              'curationUtils',
              'curationUtils.curationQueue',
              'curationUtils.reportedTraits',
              'curationUtils.studySampleReview',
              'curationUtils.unpublishStudy',
              'dataExport',
              'dataReleaseQC',
              'dataReleaseQC.functions',
              'epmcXMLTools',
              'solrIndexerManager',
              'solrIndexerManager.components',
              'solrWrapper',
              'ftpSummaryStatsScript',
              'harmonisationUtils',
              'catalogPlots',
              'log_analysis'],
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
                            'queue-harmonisation = harmonisationUtils.queue_harmonisation:main',
                            'curation-queue = curationUtils.curationQueue.curation_queue_with_ancestry:main',
                            'analyze-reported-traits = curationUtils.reportedTraits.analyze_reported_traits:main',
                            'unpublish-studies = curationUtils.unpublishStudy.unpublish_studies:main',
                            'study-design-sample-info = curationUtils.studySampleReview.check_studydesign_sampleinfo:main',
                            'data-curation-snapshot = curationUtils.data_curation_snapshot:main',
                            'peak-finder = gwasAssociationFilter.peak_finder:main',
                            'gwas-Rplotter = catalogPlots.r_plotter:main',
                            'sumstats-fetch-table = catalogPlots.SumStats_fetch_table:main',
                            'sumstats-log-parser = log_analysis.parse_sumstats_ftp_logs:main'
                            ]
    },
    license='',
    install_requires=requirements
)

from distutils.core import setup

# This script defines the installation and packaging properties for the python packages
# included in this repository


setup(
    description = 'A small module to facilitate the interaction with the GWAS Catalog solr cores.',
    name='solrWrapper',

    version='1.0',
    py_modules = ['solrWrapper'],

    author = 'Daniel Suveges',
    author_email = 'dsuveges@ebi.ac.uk',

    install_requires=['pandas', 'requests'] 
)


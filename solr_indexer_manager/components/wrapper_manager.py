import numpy as np

def call_generator(db_updates, wrapper):
    jobs = 30   # Maximum number of jobs
    pmids = [z for x in db_updates.values() for z in x ]  # List of all pubmed ID which will be submitted:

    calls = []
    for chunk in np.array_split(np.array(pmids),jobs):
        calls.append('{} -d -e -p {}'.format(wrapper, ','.join(chunk)))

    return calls
        

def trait_calls(wrapper):
    return [
        '{} -a -s -e '.format(wrapper),
        '{} -a -s -d '.format(wrapper)
    ]
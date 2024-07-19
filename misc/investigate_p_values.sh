import pandas as pd
import gzip

# Define the dtypes to optimize memory usage
dtype_dict = { 
    'chromosome': 'int', 
    'base_pair_location': 'int', 
    'effect_allele': 'str', 
    'other_allele': 'str', 
    'beta': 'float', 
    'standard_error': 'float', 
    'effect_allele_frequency': 'float', 
    'p_value': 'float', 
    'ID': 'str', 
    'INFO': 'str', 
    'n': 'int', 
    'TEST': 'str', 
    'CHISQ': 'float', 
    'EXTRA': 'str' 
}

print('Read the gzipped file into a pandas DataFrame in chunks')
with gzip.open('/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/a65_a69_other_spirochetal_diseases_NFE_combined_formatted.tsv.gz', 'rt') as file:
    chunk_size = 100000
    chunks = pd.read_csv(file, sep='\t', dtype=dtype_dict, chunksize=chunk_size, low_memory=False)

    print('Finding rows with NaN p_value and TEST_FAIL in chunks')
    rows_with_nan_p_value = []
    rows_with_test_fail = []
    for chunk in chunks:
        rows_with_nan_p_value.append(chunk[chunk['p_value'].isna()])
        rows_with_test_fail.append(chunk[chunk['EXTRA'] == 'TEST_FAIL'])

    rows_with_nan_p_value = pd.concat(rows_with_nan_p_value)
    rows_with_test_fail = pd.concat(rows_with_test_fail)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print('rows_with_nan_p_value')
print(rows_with_nan_p_value.head(50))
print(f'Number of rows with NaN p_value: {len(rows_with_nan_p_value)}')

print('rows_with_test_fail')
print(rows_with_test_fail.head(50))
print(f'Number of rows with TEST_FAIL: {len(rows_with_test_fail)}')

all_nan_rows_test_fail = rows_with_nan_p_value['EXTRA'].eq('TEST_FAIL').all()
print(f'All rows with NaN p_value have EXTRA=TEST_FAIL: {all_nan_rows_test_fail}')

print('Done!')
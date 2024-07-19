import pandas as pd

file_path = "/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/2.xlsx"
updated_file_path = "/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/2_updated.xlsx"

df = pd.read_excel(file_path)

# Rename the columns
df.columns = [
    'Study tag', 
    'Study tag transformed', 
    'Summary statistics file', 
    'Variant count', 
    'md5 sum',
    'Reported trait',
    'Cohort(s)',
]  

# Save the updated DataFrame back to Excel
df.to_excel(updated_file_path, index=False)


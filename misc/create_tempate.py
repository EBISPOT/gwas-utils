import pandas as pd

# Load the new data file
new_data_file_path = '/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/2_updated.xlsx'
df_new_data = pd.read_excel(new_data_file_path)

# Load the main study file
main_study_file_path = '/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/1_study.xlsx'
df_main_study = pd.read_excel(main_study_file_path, sheet_name='study', header=1)

# Prepare default values template
default_values = {
    'Genotyping technology': 'Whole genome sequencing',
    'Array manufacturer': '',
    'Array information': '',
    'Analysis Software': 'regenie_v3.2.5',
    'Imputation': 'No',
    'Imputation panel': '',
    'Imputation software': '',
    'Statistical model': 'Linear regression',
    'Study description': 'UKB WGS association analysis of quantitative traits',
    'Adjusted covariates': 'genetic PCs {1-20} | sex | age at baseline | sex:age | age2 | sequencing protocol',
    'Background trait': '',
    'Readme text': 'pre-print describing the study here: https://www.medrxiv.org/content/10.1101/2023.12.06.23299426v1',
    'Summary statistics assembly': 'GRCh38',
    'MAF lower limit': '',
    'Cohort(s)': 'UKBB AFR',
    'Cohort specific reference': '',
    'Sumstats': 'Yes',
    'GxE': 'No',
    'Pooled': 'No',
    'Sex': 'combined',
    'Coordinate system': '1-based'
}

# Loop through each row in the new data and insert into main study data
for _, row in df_new_data.iterrows():
    new_row = {
        'Study tag': row['Study tag'],
        'Genotyping technology': default_values['Genotyping technology'],
        'Array manufacturer': default_values['Array manufacturer'],
        'Array information': default_values['Array information'],
        'Analysis Software': default_values['Analysis Software'],
        'Imputation': default_values['Imputation'],
        'Imputation panel': default_values['Imputation panel'],
        'Imputation software': default_values['Imputation software'],
        'Variant count': row['Variant count'],
        'Statistical model': default_values['Statistical model'],
        'Study description': default_values['Study description'],
        'Adjusted covariates': default_values['Adjusted covariates'],
        'Reported trait': row['Reported trait'],
        'Background trait': default_values['Background trait'],
        'Summary statistics file': row['Summary statistics file'],
        'md5 sum': row['md5 sum'],
        'Readme text': default_values['Readme text'],
        'Summary statistics assembly': default_values['Summary statistics assembly'],
        'MAF lower limit': default_values['MAF lower limit'],
        'Cohort(s)': row['Cohort(s)'],
        'Cohort specific reference': default_values['Cohort specific reference'],
        'Sumstats': default_values['Sumstats'],
        'GxE': default_values['GxE'],
        'Pooled': default_values['Pooled'],
        'Sex': default_values['Sex'],
        'Coordinate system': default_values['Coordinate system']
    }
    
    df_main_study = pd.concat([df_main_study.iloc[:5], pd.DataFrame([new_row]), df_main_study.iloc[5:]]).reset_index(drop=True)

# Save the updated DataFrame back to the Excel file
output_file_path = '/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/1_study_updated.xlsx'
with pd.ExcelWriter(output_file_path, mode='w') as writer:
    df_main_study.to_excel(writer, sheet_name='study', index=False)

print("Excel file updated successfully.")

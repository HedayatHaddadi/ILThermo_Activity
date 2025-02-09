import os
import pandas as pd
import json
import numpy as np

# Load the dataset
base_dir = os.getcwd()
file_path = os.path.join(base_dir, 'processed_grouped_data_with_regression.csv')
processed_df = pd.read_csv(file_path)

# Select the relevant columns
group_columns = [col for col in processed_df.columns if 'ref_id_group_' in col]
group_columns.append('ref_id_seudo_group')
group_columns.extend([col for col in processed_df.columns if 'original_index_group_' in col])
group_columns.append('original_index_seudo_group')
group_columns.extend([col for col in processed_df.columns if 'temperature_group_' in col])
group_columns.append('temperature_seudo_group')
group_columns.extend([col for col in processed_df.columns if 'gamma_group_' in col])
group_columns.append('gamma_seudo_group')
group_columns.extend([col for col in processed_df.columns if 'r2_' in col])
# group_columns.append('r2_seudo_group')

# Filter the DataFrame based on the group columns
processed_df = processed_df[group_columns]

# if'gamma_seudo_group' is not None and the length of the its list is < 3 set the gamma_seudo_group to None
processed_df['gamma_seudo_group'] = processed_df['gamma_seudo_group'].apply(lambda x: None if isinstance(x, str) and len(json.loads(x)) < 3 else x)

# Function to convert string to list of floats
def str_to_float_list(s):
    return [float(i) for i in json.loads(s)]

# Calculate natural log of gamma and inverse of temperature for all groups
for col in processed_df.columns:
    if 'gamma_group_' in col or col == 'gamma_seudo_group':
        processed_df[f'ln_{col}'] = processed_df[col].apply(lambda x: [np.log(float(i)) for i in json.loads(x)] if isinstance(x, str) else x)
    if 'temperature_group_' in col or col == 'temperature_seudo_group':
        processed_df[f'inv_{col}'] = processed_df[col].apply(lambda x: [1/float(i) for i in json.loads(x)] if isinstance(x, str) else x)

# Rename seudo_group columns to the last group name
group_numbers = [int(col.split('_')[-1]) for col in processed_df.columns if col.split('_')[-1].isdigit()]
last_group_number = max(group_numbers) if group_numbers else 0
for col in processed_df.columns:
    if 'seudo_group' in col:
        new_col_name = col.replace('seudo_group', f'group_{last_group_number + 1}')
        processed_df.rename(columns={col: new_col_name}, inplace=True)

# Save the filtered DataFrame (optional)
processed_df.to_csv('filtered_grouped_data.csv', index=False)

import os
import pandas as pd

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

# Filter the DataFrame based on the group columns
processed_df = processed_df[group_columns]

# Remove rows where 'gamma_seudo_group' is not None and the length of the list is < 3
processed_df = processed_df[processed_df['gamma_seudo_group'].apply(lambda x: not isinstance(x, str) or len(eval(x)) >= 3 if x is not None else True)]

# Save the filtered DataFrame (optional)
processed_df.to_csv('filtered_grouped_data.csv', index=False)

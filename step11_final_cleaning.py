import pandas as pd
import ast

# Load datasets
processed_df = pd.read_csv("processed_with_selected_group.csv")
gh_multiple_df = pd.read_csv("gh_filtered_activity_data_multiple.csv")
gh_single_df = pd.read_csv("gh_filtered_activity_data_single.csv")
filtered_activity_df = pd.read_csv("filtered_activity_data.csv")

# Ensure 'selected_group' is treated as an integer, skip if None
processed_df['selected_group'] = processed_df['selected_group'].apply(lambda x: int(x) if pd.notnull(x) else None)

# Get the indices of all selected groups
selected_indices_multiple = []
for index, row in processed_df.iterrows():
    if pd.notnull(row['selected_group']):
        group_column = f"original_index_group_{int(row['selected_group'])}"
        indices = ast.literal_eval(row[group_column])
        selected_indices_multiple.extend(indices)

# Get all indices from 'original_index' column in gh_filtered_activity_data_single.csv
selected_indices_single = []
for index, row in gh_single_df.iterrows():
    if pd.notnull(row['original_index']):
        indices = ast.literal_eval(row['original_index'])  # Convert string representation of list to actual list
        selected_indices_single.extend(indices)

# Ensure all indices are unique and sorted
selected_indices_multiple = sorted(set(selected_indices_multiple))
selected_indices_single = sorted(set(selected_indices_single))

# Check if there is any overlap between the two sets of indices
overlap_indices = set(selected_indices_multiple).intersection(selected_indices_single)
print(f"Overlap indices count: {len(overlap_indices)}")
print(f"Overlap indices: {overlap_indices}")

# Combine the two sets of indices
combined_indices = sorted(set(selected_indices_multiple + selected_indices_single))

# Filter the 'filtered_activity_data.csv' based on the combined indices
semi_final_filtered_activity_df = filtered_activity_df[filtered_activity_df.index.isin(combined_indices)]
print(f"Filtered activity data shape: {semi_final_filtered_activity_df.shape}")


# Ensure high precision for 'gamma' and 'temperature'
semi_final_filtered_activity_df.loc[:, 'gamma'] = semi_final_filtered_activity_df['gamma'].astype(float).round(6)
semi_final_filtered_activity_df.loc[:, 'temperature'] = semi_final_filtered_activity_df['temperature'].astype(float).round(6)

# Find duplicate rows based on 'IL_id', 'solute_id', 'temperature', and 'gamma'
duplicates = semi_final_filtered_activity_df[
    semi_final_filtered_activity_df.duplicated(subset=['IL_id', 'solute_id', 'temperature', 'gamma'], keep=False)
]

# Group by 'IL_id', 'solute_id', 'temperature', and 'gamma' to get indices for each combination
duplicate_groups = duplicates.groupby(['IL_id', 'solute_id', 'temperature', 'gamma']).apply(lambda x: x.index.tolist()).reset_index(name='duplicate_indices')

# retain only the first index from each group
indices_to_remove = duplicate_groups['duplicate_indices'].apply(lambda x: x[1:]).sum()

# Remove duplicate rows from the filtered activity data
final_filtered_activity_df = semi_final_filtered_activity_df.drop(indices_to_remove)
print(f"Final filtered activity data shape: {final_filtered_activity_df.shape}")

# Save the final filtered activity data to a CSV file
final_filtered_activity_df.to_csv('final_filtered_activity_data.csv', index=False)


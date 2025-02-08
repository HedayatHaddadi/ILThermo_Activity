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

# check if there is any overlap between the two sets of indices
overlap_indices = set(selected_indices_multiple).intersection(selected_indices_single)
print(f"Overlap indices count: {len(overlap_indices)}")
print(f"Overlap indices: {overlap_indices}")

# combine the two sets of indices
combined_indices = sorted(set(selected_indices_multiple + selected_indices_single))

# filter the 'filtered_activity_data.csv' based on the combined indices
semi_final_filtered_activity_df = filtered_activity_df[filtered_activity_df.index.isin(combined_indices)]
print(f"Final filtered activity data shape: {semi_final_filtered_activity_df.shape}")






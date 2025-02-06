import os
import json
import pandas as pd
from collections import defaultdict

# Load the dataset
base_dir = os.getcwd()
file_path = os.path.join(base_dir, 'gh_filtered_activity_data_multiple.csv')
df = pd.read_csv(file_path)

def process_row(row):
    # Convert string representation of lists to actual lists
    ref_ids = json.loads(row['ref_id'])
    original_indices = json.loads(row['original_index'])
    temperatures = json.loads(row['temperature'])
    gammas = json.loads(row['gamma'])
    
    # Count occurrences of each ref_id
    ref_counts = {rid: ref_ids.count(rid) for rid in set(ref_ids)}
    
    # Initialize storage for groups
    groups = defaultdict(lambda: {'ref_id': [], 'original_index': [], 'temperature': [], 'gamma': []})
    
    # General group contains all samples
    groups['general_group'] = {
        'ref_id': ref_ids,
        'original_index': original_indices,
        'temperature': temperatures,
        'gamma': gammas
    }
    
    # Separate ref_ids into groups
    group_idx = 0
    has_sedu_group = False
    for rid, count in ref_counts.items():
        if count >= 3:
            group_name = f'group_{group_idx}'
            group_idx += 1
        else:
            group_name = 'seudo_group'
            has_sedu_group = True
        
        for i, rid_val in enumerate(ref_ids):
            if rid_val == rid:
                groups[group_name]['ref_id'].append(rid_val)
                groups[group_name]['original_index'].append(original_indices[i])
                groups[group_name]['temperature'].append(temperatures[i])
                groups[group_name]['gamma'].append(gammas[i])
    
    # Ensure all ref_ids with <3 samples are grouped under sedu_group
    if has_sedu_group:
        groups['seudo_group'] = {  # Merge all under a single sedu_group
            'ref_id': [], 'original_index': [], 'temperature': [], 'gamma': []
        }
        for rid, count in ref_counts.items():
            if count < 3:
                for i, rid_val in enumerate(ref_ids):
                    if rid_val == rid:
                        groups['seudo_group']['ref_id'].append(rid_val)
                        groups['seudo_group']['original_index'].append(original_indices[i])
                        groups['seudo_group']['temperature'].append(temperatures[i])
                        groups['seudo_group']['gamma'].append(gammas[i])
    
    return groups

# Process all rows
processed_data = []
for _, row in df.iterrows():
    processed_data.append(process_row(row))

# Convert processed data into a DataFrame format
expanded_rows = []
for i, row_groups in enumerate(processed_data):
    row_dict = {}
    for group_name, data in row_groups.items():
        for key, values in data.items():
            row_dict[f'{key}_{group_name}'] = json.dumps(values)  # Convert lists back to JSON strings
    expanded_rows.append(row_dict)

processed_df = pd.DataFrame(expanded_rows)

# Save the processed DataFrame to CSV
output_file = os.path.join(base_dir, 'processed_grouped_data.csv')
processed_df.to_csv(output_file, index=False)

print(f'Processed data saved to {output_file}')

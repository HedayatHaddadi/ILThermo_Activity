def remove_redundant(filtered_df):
    duplicates = filtered_df[
        filtered_df.duplicated(subset=['IL_id', 'solute_id', 'temperature', 'gamma', 'ref_id'], keep=False)  # to remove un-intentional duplication of an entry in dataset
    ]
    
    duplicate_groups = duplicates.groupby(['IL_id', 'solute_id', 'temperature', 'gamma', 'ref_id']).apply(lambda x: x.index.tolist()).reset_index(name='duplicate_indices')
    indices_to_remove = duplicate_groups['duplicate_indices'].apply(lambda x: x[1:]).sum()
    
    filtered_df = filtered_df.drop(indices_to_remove)
    return filtered_df
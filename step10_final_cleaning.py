import pandas as pd
import ast

def load_datasets():
    multi_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
    single_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_single.csv")
    single_df = pd.read_csv("Intermediate_Data/step8_single_ref_single_entry.csv")
    filtered_activity_df = pd.read_csv("Intermediate_Data/step7_activity_data_elements_filtered.csv")
    return multi_resolved, single_resolved, single_df, filtered_activity_df

def get_selected_indices(multi_resolved, single_resolved, single_df):
    multi_resolved['selected_group'] = multi_resolved['selected_group'].apply(lambda x: int(x) if pd.notnull(x) else None)
    
    selected_indices_multiple_res = []
    for _, row in multi_resolved.iterrows():
        if pd.notnull(row['selected_group']):
            group_column = f"original_index_group_{int(row['selected_group'])}"
            indices = ast.literal_eval(row[group_column])
            selected_indices_multiple_res.extend(indices)
    
    
    selected_indices_single_res = []
    for _, row in single_resolved.iterrows():
        if pd.notnull(row['selected_group']):
            group_column = f"original_index_group_{int(row['selected_group'])}"
            indices = ast.literal_eval(row[group_column])
            selected_indices_single_res.extend(indices)

    
    selected_indices_single = []
    for _, row in single_df.iterrows():
        if pd.notnull(row['original_index']):
            indices = ast.literal_eval(row['original_index'])
            selected_indices_single.extend(indices)
    
    selected_indices_multiple_res = sorted(set(selected_indices_multiple_res))
    selected_indices_single_res = sorted(set(selected_indices_single_res))
    selected_indices_single = sorted(set(selected_indices_single))
    return selected_indices_multiple_res, selected_indices_single_res, selected_indices_single

def filter_activity_data(filtered_activity_df, combined_indices):
    semi_final_filtered_activity_df = filtered_activity_df[filtered_activity_df.index.isin(combined_indices)]
    semi_final_filtered_activity_df.loc[:, 'gamma'] = semi_final_filtered_activity_df['gamma'].astype(float).round(6)
    semi_final_filtered_activity_df.loc[:, 'temperature'] = semi_final_filtered_activity_df['temperature'].astype(float).round(6)
    return semi_final_filtered_activity_df

def remove_duplicates(semi_final_filtered_activity_df):
    """
    Remove duplicate rows from the DataFrame based on specific columns.
    This function identifies and removes duplicate rows in the DataFrame 
    `semi_final_filtered_activity_df` based on the columns 'IL_id', 'solute_id', 
    'temperature', and 'gamma'. It keeps the first occurrence of each duplicate 
    and removes the rest.
    Args:
        semi_final_filtered_activity_df (pd.DataFrame): The DataFrame from which 
        duplicates need to be removed.
    Returns:
        pd.DataFrame: A DataFrame with duplicates removed.
    # to remove similar rows with different ref_id. this is different from the previous step where we removed rows with same ref_id in remove_redundant function.
    """
    """
    The reason for this function at this stage is to not remove supporting and 
    in agreement data from different ref_ids before Gibbs-Helmholtz processing.
    """

    duplicates = semi_final_filtered_activity_df[
        semi_final_filtered_activity_df.duplicated(subset=['IL_id', 'solute_id', 'temperature', 'gamma'], keep=False) 
    ]
    
    duplicate_groups = duplicates.groupby(['IL_id', 'solute_id', 'temperature', 'gamma']).apply(lambda x: x.index.tolist()).reset_index(name='duplicate_indices')
    indices_to_remove = duplicate_groups['duplicate_indices'].apply(lambda x: x[1:]).sum()
    
    final_filtered_activity_df = semi_final_filtered_activity_df.drop(indices_to_remove)
    print(f"Removed {len(indices_to_remove)} duplicate rows.")
    return final_filtered_activity_df


def update_ref_ids(df):
    
    initial_ref_file = "Intermediate_Data/step7_initial_ref_ids.csv"
    output_ref_file = "Intermediate_Data/step10_final_ref_ids.csv"
    # Load the initial ref_id mapping
    initial_ref_df = pd.read_csv(initial_ref_file)
    
    # Get unique references in the final dataset
    remaining_refs = df['ref_id'].unique()
    
    # Create a new continuous ref_id mapping
    new_ref_id_mapping = {old_id: new_id for new_id, old_id in enumerate(sorted(remaining_refs), start=1)}
    
    # Update ref_id in the final dataframe
    df['ref_id'] = df['ref_id'].map(new_ref_id_mapping)
    # remove original_index column
    df.drop(columns=['original_index'], inplace=True)
    
    # Update and save the new ref_id mapping
    filtered_ref_df = initial_ref_df[initial_ref_df['ref_id'].isin(remaining_refs)].copy()
    filtered_ref_df['ref_id'] = filtered_ref_df['ref_id'].map(new_ref_id_mapping)
    filtered_ref_df.to_csv(output_ref_file, index=False)
    
    print("Updated ref_id values and saved new mapping.")

    return df




def finalizing_data():
    multi_resolved, single_resolved, single_df, filtered_activity_df = load_datasets()
    selected_indices_multiple_res, selected_indices_single_res, selected_indices_single = get_selected_indices(multi_resolved, single_resolved, single_df)
    
    overlap_multiple_single_res = set(selected_indices_multiple_res).intersection(selected_indices_single_res)
    overlap_multiple_single = set(selected_indices_multiple_res).intersection(selected_indices_single)
    overlap_single_res_single = set(selected_indices_single_res).intersection(selected_indices_single)
    
    print(f"Overlap between multiple resolved and single resolved: {len(overlap_multiple_single_res)}")
    print(f"Overlap between multiple resolved and single: {len(overlap_multiple_single)}")
    print(f"Overlap between single resolved and single: {len(overlap_single_res_single)}")
    
    combined_indices = sorted(set(selected_indices_multiple_res + selected_indices_single_res + selected_indices_single))
    
    semi_final_filtered_activity_df = filter_activity_data(filtered_activity_df, combined_indices)
    print(f"Filtered activity data shape: {semi_final_filtered_activity_df.shape}")
    
    final_filtered_activity_df = remove_duplicates(semi_final_filtered_activity_df)
    
    final_filtered_activity_df = update_ref_ids(final_filtered_activity_df)
    print(f"Final filtered activity data shape: {final_filtered_activity_df.shape}")

    final_filtered_activity_df.to_csv('Intermediate_Data/step10_final_refined_activity_dataset.csv', index=False)
    return final_filtered_activity_df

if __name__ == "__main__":
    finalizing_data()

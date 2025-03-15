import pandas as pd
import ast

def load_datasets():
    multi_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
    single_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_single.csv")
    single_df = pd.read_csv("Intermediate_Data/step8_single_ref_single_entry.csv")
    filtered_activity_df = pd.read_csv("Intermediate_Data/step7_activity_data_elements_filtered.csv")
    return multi_resolved, single_resolved, single_df, filtered_activity_df



def get_selected_indices(multi_resolved, single_resolved, single_df):
    def extract_sorted_indices(df):
        # Identify the correct original_index_group_ column based on selected_group
        def get_original_index(row):
            if pd.notna(row['selected_group']):  # Ensure selected_group is not None
                col_name = f'original_index_group_{int(row["selected_group"])}'
                return eval(row[col_name]) if col_name in df.columns else []
            return []

        # Apply the function to extract indices
        df['extracted_indices'] = df.apply(get_original_index, axis=1)

        # Flatten, convert to int, get unique values, and sort
        sorted_indices = sorted(set(int(i) for sublist in df['extracted_indices'] for i in sublist))
        
        return sorted_indices

    # Extract sorted indices separately for multi_resolved and single_resolved
    multi_resolved_indices = extract_sorted_indices(multi_resolved)
    single_resolved_indices = extract_sorted_indices(single_resolved)

    # Extract sorted indices for single_df
    single_df['original_index'] = single_df['original_index'].apply(eval)  # Convert string representation to list
    single_df_indices = sorted(single_df.explode('original_index')['original_index'].astype(int).unique())

    return multi_resolved_indices, single_resolved_indices, single_df_indices




def filter_activity_data(filtered_activity_df, combined_indices):
    semi_final_filtered_activity_df = filtered_activity_df[filtered_activity_df['original_index'].astype(int).isin(combined_indices)]
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
    probably some of the rows have been duplicated for a specific entry_id. 
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
    multi_resolved_indices, single_resolved_indices, single_df_indices = get_selected_indices(multi_resolved, single_resolved, single_df)
    
    overlap_multiple_single_res = set(multi_resolved_indices).intersection(single_resolved_indices)
    overlap_multiple_single = set(multi_resolved_indices).intersection(single_df_indices)
    overlap_single_res_single = set(single_resolved_indices).intersection(single_df_indices)
    
    print(f"Overlap between multiple resolved and single resolved: {len(overlap_multiple_single_res)}")
    print(f"Overlap between multiple resolved and single: {len(overlap_multiple_single)}")
    print(f"Overlap between single resolved and single: {len(overlap_single_res_single)}")
    
    combined_indices = sorted(set(multi_resolved_indices + single_resolved_indices + single_df_indices))
    
    semi_final_filtered_activity_df = filter_activity_data(filtered_activity_df, combined_indices)
    print(f"Filtered activity data shape: {semi_final_filtered_activity_df.shape}")
    
    final_filtered_activity_df = remove_duplicates(semi_final_filtered_activity_df)
    
    final_filtered_activity_df = update_ref_ids(final_filtered_activity_df)
    print(f"Final filtered activity data shape: {final_filtered_activity_df.shape}")

    final_filtered_activity_df.to_csv('Intermediate_Data/step10_final_refined_activity_dataset.csv', index=False)
    return final_filtered_activity_df

if __name__ == "__main__":
    finalizing_data()

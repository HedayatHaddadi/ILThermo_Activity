import pandas as pd



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


single_df = pd.read_csv("Intermediate_Data/step8_single_ref_single_entry.csv")
multi_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
single_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_single.csv")


multi_resolved_indices, single_resolved_indices, single_df_indices = get_selected_indices(multi_resolved, single_resolved, single_df)

indices = [52414, 52415, 43180, 43181, 43182, 43183, 53089]


print(any(i in multi_resolved_indices for i in indices))  
print(all(i in multi_resolved_indices for i in indices))  
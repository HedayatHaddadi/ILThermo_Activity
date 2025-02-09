import pandas as pd
import ast

def load_datasets():
    processed_df = pd.read_csv("step10_processed_with_selected_group.csv")
    gh_multiple_df = pd.read_csv("step8_gh_filtered_activity_data_multiple.csv")
    gh_single_df = pd.read_csv("step8_gh_filtered_activity_data_single.csv")
    filtered_activity_df = pd.read_csv("step7_filtered_activity_data.csv")
    return processed_df, gh_multiple_df, gh_single_df, filtered_activity_df

def get_selected_indices(processed_df, gh_single_df):
    processed_df['selected_group'] = processed_df['selected_group'].apply(lambda x: int(x) if pd.notnull(x) else None)
    
    selected_indices_multiple = []
    for _, row in processed_df.iterrows():
        if pd.notnull(row['selected_group']):
            group_column = f"original_index_group_{int(row['selected_group'])}"
            indices = ast.literal_eval(row[group_column])
            selected_indices_multiple.extend(indices)
    
    selected_indices_single = []
    for _, row in gh_single_df.iterrows():
        if pd.notnull(row['original_index']):
            indices = ast.literal_eval(row['original_index'])
            selected_indices_single.extend(indices)
    
    selected_indices_multiple = sorted(set(selected_indices_multiple))
    selected_indices_single = sorted(set(selected_indices_single))
    
    return selected_indices_multiple, selected_indices_single

def filter_activity_data(filtered_activity_df, combined_indices):
    semi_final_filtered_activity_df = filtered_activity_df[filtered_activity_df.index.isin(combined_indices)]
    semi_final_filtered_activity_df.loc[:, 'gamma'] = semi_final_filtered_activity_df['gamma'].astype(float).round(6)
    semi_final_filtered_activity_df.loc[:, 'temperature'] = semi_final_filtered_activity_df['temperature'].astype(float).round(6)
    return semi_final_filtered_activity_df

def remove_duplicates(semi_final_filtered_activity_df):
    duplicates = semi_final_filtered_activity_df[
        semi_final_filtered_activity_df.duplicated(subset=['IL_id', 'solute_id', 'temperature', 'gamma'], keep=False)
    ]
    
    duplicate_groups = duplicates.groupby(['IL_id', 'solute_id', 'temperature', 'gamma']).apply(lambda x: x.index.tolist()).reset_index(name='duplicate_indices')
    indices_to_remove = duplicate_groups['duplicate_indices'].apply(lambda x: x[1:]).sum()
    
    final_filtered_activity_df = semi_final_filtered_activity_df.drop(indices_to_remove)
    return final_filtered_activity_df

def main():
    processed_df, gh_multiple_df, gh_single_df, filtered_activity_df = load_datasets()
    
    selected_indices_multiple, selected_indices_single = get_selected_indices(processed_df, gh_single_df)
    
    overlap_indices = set(selected_indices_multiple).intersection(selected_indices_single)
    print(f"Overlap indices count: {len(overlap_indices)}")
    print(f"Overlap indices: {overlap_indices}")
    
    combined_indices = sorted(set(selected_indices_multiple + selected_indices_single))
    
    semi_final_filtered_activity_df = filter_activity_data(filtered_activity_df, combined_indices)
    print(f"Filtered activity data shape: {semi_final_filtered_activity_df.shape}")
    
    final_filtered_activity_df = remove_duplicates(semi_final_filtered_activity_df)
    print(f"Final filtered activity data shape: {final_filtered_activity_df.shape}")
    
    final_filtered_activity_df.to_csv('step11_activity_dataset.csv', index=False)

if __name__ == "__main__":
    main()

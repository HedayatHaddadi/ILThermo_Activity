import ast
import pandas as pd


def load_datasets():
    multi_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
    single_resolved = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_single.csv")
    single_df = pd.read_csv("Intermediate_Data/step8_single_ref_single_entry.csv")
    filtered_activity_df = pd.read_csv("Intermediate_Data/step7_activity_data_elements_filtered.csv")
    final_df = pd.read_csv("Intermediate_Data/step10_final_refined_activity_dataset.csv")
    return multi_resolved, single_resolved, single_df, filtered_activity_df, final_df

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


if __name__ == "__main__":
    multi_resolved, single_resolved, single_df, filtered_activity_df, final_df = load_datasets()
    selected_indices_multiple_res, selected_indices_single_res, selected_indices_single = get_selected_indices(multi_resolved, single_resolved, single_df)
    # filter the filtered_activity_df based on the selected indices of selected_indices_single
    filtered_activity_df = filtered_activity_df[filtered_activity_df.index.isin(selected_indices_single)]
    # print shape of filtered_activity_df
    print(filtered_activity_df.shape)
    # get the sum of column population in single_df
    print(single_df['population'].sum())
    # filter the filtered_activity_df based on the selected indices of selected_indices_multiple_res
    filtered_activity_df_mul = filtered_activity_df[filtered_activity_df.index.isin(selected_indices_multiple_res)]
    # # filter the filtered_activity_df based on the selected indices of selected_indices_single_res
    filtered_activity_df_single_res = filtered_activity_df[filtered_activity_df.index.isin(selected_indices_single_res)] 
    # # filter the filtered_activity_df based on the selected indices of selected_indices_single
    filtered_activity_df_single = filtered_activity_df[filtered_activity_df.index.isin(selected_indices_single)]

    # get the unique combinations of SMILES_IL, SMILES_solute in filtered_activity_df_mul
    unique_combinations_mul = filtered_activity_df_mul[['SMILES_IL', 'SMILES_solute']].drop_duplicates()

    # get the unique combinations of SMILES_IL, SMILES_solute in filtered_activity_df_single_res
    unique_combinations_single_res = filtered_activity_df_single_res[['SMILES_IL', 'SMILES_solute']].drop_duplicates()

    # get the unique combinations of SMILES_IL, SMILES_solute in filtered_activity_df_single
    unique_combinations_single = filtered_activity_df_single[['SMILES_IL', 'SMILES_solute']].drop_duplicates()

    # check if there is any common SMILES_IL, SMILES_solute between filtered_activity_df_mul and filtered_activity_df_single_res
    common_mul_single_res = pd.merge(unique_combinations_mul, unique_combinations_single_res, on=['SMILES_IL', 'SMILES_solute'], how='inner')
    print("Common combinations between multiple resolved and single resolved:", common_mul_single_res)

    # check if there is any common SMILES_IL, SMILES_solute between filtered_activity_df_mul and filtered_activity_df_single
    common_mul_single = pd.merge(unique_combinations_mul, unique_combinations_single, on=['SMILES_IL', 'SMILES_solute'], how='inner')
    print("Common combinations between multiple resolved and single:", common_mul_single)

    # check if there is any common SMILES_IL, SMILES_solute between filtered_activity_df_single_res and filtered_activity_df_single
    common_single_res_single = pd.merge(unique_combinations_single_res, unique_combinations_single, on=['SMILES_IL', 'SMILES_solute'], how='inner')
    print("Common combinations between single resolved and single:", common_single_res_single)
    # sum of len indices in selected_indices_multiple_res, selected_indices_single_res, selected_indices_single
    print("Sum of lengths of selected indices:", sum(len(indices) for indices in [selected_indices_multiple_res, selected_indices_single_res, selected_indices_single]))
    print("Length of final_df:", len(final_df))
    print("Difference (removed duplicated samples):",  sum(len(indices) for indices in [selected_indices_multiple_res, selected_indices_single_res, selected_indices_single]) - len(final_df))
     

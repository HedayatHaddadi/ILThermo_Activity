import pandas as pd

def load_dataset(file_path):
    return pd.read_csv(file_path)

def initialize_columns(df):
    columns_to_add = ['SMILES_IL', 'SMILES_solute', 'IL_name', 'solute_name', 'IL_id', 'solute_id']
    for column in columns_to_add:
        df[column] = 'NaN'
    return df

def is_ionic_liquid(smiles):
    return isinstance(smiles, str) and ("." in smiles and "+" in smiles and "-")

def assign_smiles_and_ids(df):
    for index, row in df.iterrows():
        smiles_1, smiles_2 = row['cmp1_smiles'], row['cmp2_smiles']
        name_1, name_2 = row['cmp1_name'], row['cmp2_name']
        id_1, id_2 = row['cmp1_id'], row['cmp2_id']

        if is_ionic_liquid(smiles_1):
            df.at[index, 'SMILES_IL'] = smiles_1
            df.at[index, 'IL_name'] = name_1
            df.at[index, 'IL_id'] = id_1
            df.at[index, 'SMILES_solute'] = smiles_2
            df.at[index, 'solute_name'] = name_2
            df.at[index, 'solute_id'] = id_2
        elif is_ionic_liquid(smiles_2):
            df.at[index, 'SMILES_IL'] = smiles_2
            df.at[index, 'IL_name'] = name_2
            df.at[index, 'IL_id'] = id_2
            df.at[index, 'SMILES_solute'] = smiles_1
            df.at[index, 'solute_name'] = name_1
            df.at[index, 'solute_id'] = id_1
    return df

def filter_dicationic_compounds(df):
    def is_dicationic(smiles):
        return smiles.count('+') > 1 or smiles.count('-') > 1 or smiles.count('.') > 1

    dicationic_df = df[df['SMILES_IL'].apply(is_dicationic)]
    df = df[~df['SMILES_IL'].apply(is_dicationic)]
    return df, dicationic_df

def sanity_check(df):
    missing_il = df['SMILES_IL'] == 'NaN'
    missing_solute = df['SMILES_solute'] == 'NaN'

    if missing_il.any() or missing_solute.any():
        print(f"Warning: {missing_il.sum()} IL SMILES and {missing_solute.sum()} solute SMILES were not assigned!")
    else:
        print("All SMILES have been assigned.")

def save_dataset(df, output_file):
    df.to_csv(output_file, index=False)
    print(f"Processing complete. Updated file saved as {output_file}.")

def save_removed_rows(df, output_file):
    df.to_csv(output_file, index=False)
    print(f"Removed rows saved as {output_file}.")

def place_smiles(df):   
    output_file = "step5_updated_activity_data_filled_place_smiles.csv"
    removed_rows_file = "step5_removed_dicationic_rows.csv"
    df = initialize_columns(df)
    df = assign_smiles_and_ids(df)
    df, removed_rows_df = filter_dicationic_compounds(df)
    sanity_check(df)
    save_dataset(df, output_file)
    save_removed_rows(removed_rows_df, removed_rows_file)
    return df

if __name__ == "__main__":
    file_path = "step4_updated_activity_data_filled.csv"
    df = load_dataset(file_path)
    place_smiles(df)

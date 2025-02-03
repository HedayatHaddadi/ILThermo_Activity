import pandas as pd
import ilthermopy as ilt
from tqdm import tqdm

def read_data(file_path):
    return pd.read_csv(file_path)

def filter_nan_rows(df):
    nan_rows = df[df['cmp1_smiles'].isna() | df['cmp2_smiles'].isna()]
    nan_rows.to_csv('nan_rows.csv', index=False)
    return nan_rows['id'].unique()

def fetch_entry_data(nan_rows_id):
    entry_data = []
    for id in tqdm(nan_rows_id, desc="Fetching ILThermo Data", unit="id"):
        entry = ilt.GetEntry(id)
        cmp1, cmp2 = entry.components[0], entry.components[1]
        entry_data.append([
            id, 
            cmp1.id, cmp1.name, cmp1.formula, cmp1.smiles, cmp1.smiles_error, cmp1.sample, cmp1.mw,
            cmp2.id, cmp2.name, cmp2.formula, cmp2.smiles, cmp2.smiles_error, cmp2.sample, cmp2.mw
        ])
    return entry_data

def create_dataframe(entry_data):
    columns = [
        "id", "cmp1_id", "cmp1_name", "cmp1_formula", "cmp1_smiles", "cmp1_smiles_error", "cmp1_sample", "cmp1_mw",
        "cmp2_id", "cmp2_name", "cmp2_formula", "cmp2_smiles", "cmp2_smiles_error", "cmp2_sample", "cmp2_mw"
    ]
    return pd.DataFrame(entry_data, columns=columns), columns  # Return both DataFrame and columns list

def merge_data(df, smiles_resolved, columns):
    df_filled = df.merge(smiles_resolved, on='id', how='left', suffixes=('', '_resolved'))
    
    for column in columns[1:]:  # Skip "id" since it is not missing
        df_filled[column] = df_filled[column].fillna(df_filled[column + '_resolved']).infer_objects(copy=False)
    
    df_filled.drop(columns=[col for col in df_filled if col.endswith('_resolved')], inplace=True)
    
    # Explicitly infer object types to avoid future downcasting issues
    df_filled = df_filled.infer_objects(copy=False)
    
    return df_filled


def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def main():
    file_path = 'updated_activity_data.csv'
    df = read_data(file_path)
    nan_rows_id = filter_nan_rows(df)
    entry_data = fetch_entry_data(nan_rows_id)
    smiles_resolved, columns = create_dataframe(entry_data)  # Get both DataFrame and columns list
    df_filled = merge_data(df, smiles_resolved, columns)
    save_data(df_filled, 'updated_activity_data_filled.csv')

if __name__ == "__main__":
    main()

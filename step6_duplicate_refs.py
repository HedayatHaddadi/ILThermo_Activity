import os
import pandas as pd
import re

def load_csv(file_path):
    return pd.read_csv(file_path, dtype=str)

def ensure_column_exists(df, column_name):
    if column_name not in df.columns:
        raise KeyError(f"The CSV file must contain a '{column_name}' column.")

def extract_title(ref_text):
    match = re.search(r"'title':\s*'([^']+)'|\"title\":\s*\"([^\"]+)\"", str(ref_text))
    return match.group(1) if match and match.group(1) else match.group(2) if match else None

def get_unique_refs(df):
    unique_refs = df[['ref']].drop_duplicates().copy()
    unique_refs['title'] = unique_refs['ref'].apply(extract_title)
    return unique_refs

def find_duplicate_titles(unique_refs):
    duplicate_titles = unique_refs[unique_refs.duplicated('title', keep=False)]
    refs_to_remove = duplicate_titles.duplicated('title', keep='first')
    return duplicate_titles.reset_index(drop=True), refs_to_remove.reset_index(drop=True)

def remove_duplicate_refs(df, removed_refs):
    return df[~df['ref'].isin(removed_refs)]

def save_to_csv(df, file_path):
    df.to_csv(file_path, index=False)

def duplicate_refs(df):

    ensure_column_exists(df, 'ref')
    
    unique_refs = get_unique_refs(df)
    duplicate_titles, refs_to_remove = find_duplicate_titles(unique_refs)
    
    removed_refs = duplicate_titles[refs_to_remove]['ref']
    removed_rows = df[df['ref'].isin(removed_refs)]
    df_filtered = remove_duplicate_refs(df, removed_refs)
    intermediate_dir = os.path.join(os.getcwd(), 'Intermediate_Data')
    removed_rows_file = os.path.join(intermediate_dir, 'step6_removed_rows_for_duplicate_refs.csv')
    removed_refs_file = os.path.join(intermediate_dir, 'step6_removed_refs_for_duplicate_refs.csv')
    output_file = os.path.join(intermediate_dir, 'step6_activity_data_removed_duplicate_refs.csv')
    
    save_to_csv(removed_rows, removed_rows_file)
    save_to_csv(removed_refs, removed_refs_file)
    save_to_csv(df_filtered, output_file)
    
    print(f"Total rows removed: {len(removed_rows)}")
    print(f"Removed rows saved to: {removed_rows_file}")
    print(f"Removed references saved to: {removed_refs_file}")
    print(f"Updated dataset saved to: {output_file}")
    return df_filtered

if __name__ == "__main__":
    file_path = 'Intermediate_Data/step5_place_smiles_for_IL_and_solute.csv'
    df = load_csv(file_path)
    duplicate_refs(df)

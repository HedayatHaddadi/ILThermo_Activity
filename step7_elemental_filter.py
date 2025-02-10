import pandas as pd
from rdkit import Chem

# Define allowed elements
ALLOWED_ELEMENTS = {'C', 'H', 'O', 'N', 'P', 'S', 'B', 'F', 'Cl', 'Br', 'I'}

# File paths
INPUT_FILE_PATH = 'step6_cleaned_activity_data.csv'
OUTPUT_FILE_PATH = 'step7_filtered_activity_data.csv'

def load_dataset(file_path):
    """Load dataset with dtype=str to avoid mixed type warnings."""
    return pd.read_csv(file_path, dtype=str, low_memory=False)

def get_periodic_table():
    """Get RDKit's periodic table."""
    return Chem.GetPeriodicTable()

def extract_elements(smiles, ptable):
    """Extract elements from SMILES using RDKit."""
    if isinstance(smiles, str):
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            return {ptable.GetElementSymbol(atom.GetAtomicNum()) for atom in mol.GetAtoms()}
    return set()

def is_valid_row(smiles_il, smiles_solute, allowed_elements, ptable):
    """Check if a row should be retained based on allowed elements."""
    elements_il = extract_elements(smiles_il, ptable)
    elements_solute = extract_elements(smiles_solute, ptable)
    return not (elements_il - allowed_elements or elements_solute - allowed_elements)

def filter_dataset(df, allowed_elements, ptable):
    """Filter rows that only contain allowed elements."""
    return df[df.apply(lambda row: is_valid_row(row.get('SMILES_IL', ''), row.get('SMILES_solute', ''), allowed_elements, ptable), axis=1)]

def elemental_filtering(df):
    """Process the dataset and save the filtered data."""
    
    output_file_path = 'step7_filtered_activity_data.csv'
    allowed_elements = {'C', 'H', 'O', 'N', 'P', 'S', 'B', 'F', 'Cl', 'Br', 'I'}

    ptable = get_periodic_table()
    filtered_df = filter_dataset(df, allowed_elements, ptable)
    
    # Retain only the specified columns and rename 'id' to 'entry_id'
    filtered_df = filtered_df[['id', 'ref', 'temperature', 'gamma', 'SMILES_IL', 'SMILES_solute', 'IL_name', 'solute_name', 'IL_id', 'solute_id']]
    filtered_df.rename(columns={'id': 'entry_id'}, inplace=True)
    
    # Create a new column 'original_index' starting from 0
    filtered_df.insert(0, 'original_index', range(len(filtered_df)))
    
    # Reorder columns
    ref_values = filtered_df['ref'].unique()

    ref_values_df = pd.DataFrame(ref_values, columns=['ref'])
    ref_values_df['ref_id'] = range(1, len(ref_values_df) + 1)
    ref_values_df = ref_values_df[['ref_id', 'ref']]
    ref_values_df.to_csv('Intermediate_Data/step7_initial_ref_ids.csv', index=False)
    

    
    # Merge 'ref_id' back into the filtered dataset
    filtered_df = filtered_df.merge(ref_values_df, on='ref')
    filtered_df = filtered_df[['original_index', 'entry_id', 'ref_id', 'IL_id', 'solute_id', 'SMILES_IL', 'SMILES_solute', 'IL_name', 'solute_name', 'temperature', 'gamma']]

    # Save the filtered dataset
    output_file_path = 'Intermediate_Data/step7_activity_data_elements_filtered.csv'
    filtered_df.to_csv(output_file_path, index=False)
    
    print(f"Processing complete. Filtered dataset saved as '{output_file_path}'.")
    print(f"Removed {len(df) - len(filtered_df)} rows containing disallowed elements.")
    return filtered_df

if __name__ == "__main__":
    input_file_path = 'step6_cleaned_activity_data.csv'
    df = load_dataset(input_file_path)
    elemental_filtering(df)

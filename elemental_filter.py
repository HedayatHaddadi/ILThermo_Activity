import pandas as pd
from rdkit import Chem

# Define allowed elements
allowed_elements = {'C', 'H', 'O', 'N', 'P', 'S', 'B', 'F', 'Cl', 'Br', 'I'}

# Load dataset with dtype=str to avoid mixed type warnings
file_path = 'updated_activity_data_filled_place_smiles.csv'
df = pd.read_csv(file_path, dtype=str, low_memory=False)

# Get RDKit's periodic table
ptable = Chem.GetPeriodicTable()

# Function to extract elements from SMILES using RDKit
def extract_elements(smiles):
    if isinstance(smiles, str):  # Ensure it's a valid string
        mol = Chem.MolFromSmiles(smiles)
        if mol:  # Ensure valid molecule
            return {ptable.GetElementSymbol(atom.GetAtomicNum()) for atom in mol.GetAtoms()}
    return set()

# Function to check if a row should be retained
def is_valid_row(smiles_il, smiles_solute):
    elements_il = extract_elements(smiles_il)
    elements_solute = extract_elements(smiles_solute)
    
    # If either SMILES contains a disallowed element, remove the row
    if elements_il - allowed_elements or elements_solute - allowed_elements:
        return False
    return True

# Filter rows that only contain allowed elements
filtered_df = df[df.apply(lambda row: is_valid_row(row.get('SMILES_IL', ''), row.get('SMILES_solute', '')), axis=1)]

# Retain only the specified columns and rename 'id' to 'entry_id'
filtered_df = filtered_df[['id', 'ref', 'temperature', 'gamma', 'SMILES_IL', 'SMILES_solute', 'IL_name', 'solute_name', 'IL_id', 'solute_id']]
filtered_df.rename(columns={'id': 'entry_id'}, inplace=True)

# Create a new column 'original_id' starting from 0
filtered_df.insert(0, 'original_id', range(len(filtered_df)))

# Reorder columns
filtered_df = filtered_df[['original_id', 'entry_id', 'ref', 'IL_id', 'solute_id', 'SMILES_IL', 'SMILES_solute', 'IL_name', 'solute_name', 'temperature', 'gamma']]

# Save the filtered dataset
filtered_df.to_csv('filtered_activity_data.csv', index=False)

print(f"Processing complete. Filtered dataset saved as 'filtered_activity_data.csv'.")
print(f"Removed {len(df) - len(filtered_df)} rows containing disallowed elements.")

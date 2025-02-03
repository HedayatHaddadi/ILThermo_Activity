import pandas as pd
import ilthermopy as ilt
from tqdm import tqdm  # Import tqdm for the progress bar

# -------------------- Read Data --------------------
file_path = 'updated_activity_data.csv'
df = pd.read_csv(file_path)

# -------------------- Filter Rows with NaN --------------------
nan_rows = df[df['cmp1_smiles'].isna() | df['cmp2_smiles'].isna()]
nan_rows.to_csv('nan_rows.csv', index=False)

# Get unique ids for entries with NaN values in the required columns
nan_rows_id = nan_rows['id'].unique()

# -------------------- Fetch Data for Entries --------------------
entry_data = []

# Use tqdm to show progress bar
for id in tqdm(nan_rows_id, desc="Fetching ILThermo Data", unit="id"):
    entry = ilt.GetEntry(id)
    cmp1 = entry.components[0]
    cmp2 = entry.components[1]
    
    # Extracting required details for cmp1 and cmp2
    entry_data.append([
        id, 
        cmp1.id, cmp1.name, cmp1.formula, cmp1.smiles, cmp1.smiles_error, cmp1.sample, cmp1.mw,
        cmp2.id, cmp2.name, cmp2.formula, cmp2.smiles, cmp2.smiles_error, cmp2.sample, cmp2.mw
    ])

# -------------------- Convert to DataFrame --------------------
columns = [
    "id", "cmp1_id", "cmp1_name", "cmp1_formula", "cmp1_smiles", "cmp1_smiles_error", "cmp1_sample", "cmp1_mw",
    "cmp2_id", "cmp2_name", "cmp2_formula", "cmp2_smiles", "cmp2_smiles_error", "cmp2_sample", "cmp2_mw"
]

smiles_resolved = pd.DataFrame(entry_data, columns=columns)

# save to csv
smiles_resolved.to_csv('smiles_resolved.csv', index=False)





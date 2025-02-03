import ilthermopy as ilt
import pandas as pd
from tqdm import tqdm  # Import tqdm for progress bar

file_path = "raw_activity_data.csv"
df = pd.read_csv(file_path)

# Get unique ids from the dataset
unique_ids = df['id'].unique()

# -------------------- Extract component details --------------------
component_details = []

# Use tqdm for progress bar
for idx in tqdm(unique_ids, desc="Fetching ILThermo data"):
    entry = ilt.GetEntry(idx)
    cmp1, cmp2 = entry.components[0], entry.components[1]
    
    # Append component details for cmp1 and cmp2
    component_details.append([
        idx,  # Include the id for each row
        cmp1.id, cmp1.name, cmp1.formula, cmp1.smiles, cmp1.smiles_error, cmp1.sample, cmp1.mw,
        cmp2.id, cmp2.name, cmp2.formula, cmp2.smiles, cmp2.smiles_error, cmp2.sample, cmp2.mw
    ])

# -------------------- Convert component details to DataFrame --------------------
columns = [
    "id", "cmp1_id", "cmp1_name", "cmp1_formula", "cmp1_smiles", "cmp1_smiles_error", "cmp1_sample", "cmp1_mw",
    "cmp2_id", "cmp2_name", "cmp2_formula", "cmp2_smiles", "cmp2_smiles_error", "cmp2_sample", "cmp2_mw"
]
components_df = pd.DataFrame(component_details, columns=columns)

# -------------------- Merge with original data --------------------
# Merge the new component details with the original data based on 'id'
df = df.merge(components_df, on='id', how='left')

# -------------------- Save the updated dataset --------------------
df.to_csv("updated_activity_data_new.csv", index=False)

print("Data extraction complete! Saved as 'updated_activity_data_new.csv'")

### Step 7: **elemental_filtering.py**

This script filters a dataset to retain only rows that contain specified allowed elements in their SMILES representations. It also removes redundant rows based on a set of columns and assigns unique reference IDs.

**Key Functions:**

1. **`load_dataset`**:
   - Loads the dataset from a CSV file into a Pandas DataFrame, ensuring that all columns are read as strings.

2. **`get_periodic_table`**:
   - Retrieves the periodic table from RDKit.

3. **`extract_elements`**:
   - Extracts elements from a given SMILES string using RDKit and returns them as a set of element symbols.

4. **`is_valid_row`**:
   - Checks if a row contains only allowed elements (from the provided set) in both the ionic liquid (IL) and solute SMILES.

5. **`filter_dataset`**:
   - Filters the dataset to include only rows where both IL and solute contain allowed elements.

6. **`remove_redundant`**:
   - Identifies and removes redundant rows from the dataset based on the columns: 'IL_id', 'solute_id', 'temperature', 'gamma', and 'ref_id'.
   - Keeps only one entry for each unique combination of these columns.

7. **`elemental_filtering`**:
   - Main function that applies elemental filtering, removes redundant rows, and assigns reference IDs to unique references.
   - The dataset is saved to a CSV file (`step7_activity_data_elements_filtered.csv`) and intermediate data is stored.

**Parameters and Thresholds:**

- **Allowed Elements:**
  - `{ 'C', 'H', 'O', 'N', 'P', 'S', 'B', 'F', 'Cl', 'Br', 'I' }`

- **Input:**
  - `df`: The Pandas DataFrame containing the dataset (`step6_activity_data_removed_duplicate_refs.csv`).

- **Output:**
  - The filtered dataset, saved as `step7_activity_data_elements_filtered.csv`.
  - The reference ID mapping saved as `step7_initial_ref_ids.csv`.

**Execution Flow:**

1. Load dataset from CSV.
2. Filter rows based on allowed elements.
3. Remove redundant rows.
4. Assign unique `ref_id` to each reference.
5. Save filtered dataset and reference ID mappings to CSV files.

**Dependencies:**
- `pandas`: For data manipulation.
- `rdkit`: For SMILES parsing and periodic table access.

**Notes:**
- The script assumes that the columns `SMILES_IL` and `SMILES_solute` are present for extracting elements from SMILES.
- A new `original_index` is generated to track the original order of the rows.

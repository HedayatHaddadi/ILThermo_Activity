### Step 4: **missing_smiles.py**

This script handles the missing SMILES data for components in the dataset. It identifies rows with missing SMILES values for components, fetches the necessary data from ILThermo, and updates the dataset with the resolved SMILES information. The updated dataset is then saved to a CSV file.

**Key Functions:**

1. **`read_data`**:
   - Reads the CSV file and returns a Pandas DataFrame.

2. **`filter_nan_rows`**:
   - Filters rows where either `cmp1_smiles` or `cmp2_smiles` is missing (`NaN`).
   - Saves the rows with missing SMILES to a separate CSV file (`step4_missing_smiles_rows.csv`).
   - Returns the unique IDs of rows with missing SMILES.

3. **`fetch_entry_data`**:
   - Fetches ILThermo data for a list of IDs that have missing SMILES.
   - Extracts component details (ID, name, formula, SMILES, error, sample, molecular weight) for both components.

4. **`create_smiles_resolved_df`**:
   - Converts the fetched ILThermo entry data into a DataFrame.
   - The DataFrame contains component details such as SMILES and molecular weight.

5. **`merge_and_fill_data`**:
   - Merges the resolved SMILES data with the original dataset (`df`).
   - Fills missing SMILES data in the original dataset with the resolved values.
   - Drops the extra resolved columns after merging.

6. **`save_data`**:
   - Saves the updated dataset to a CSV file (`step4_missing_smiles_added.csv`).

7. **`missing_smiles`**:
   - Coordinates the process of resolving missing SMILES by:
     - Filtering rows with missing SMILES.
     - Fetching ILThermo data.
     - Merging the resolved data with the original dataset.
     - Saving the updated dataset to a file.

**Parameters and Thresholds:**

- **Input:**
  - `df`: The Pandas DataFrame containing the data (`step3_smiles_added.csv`).
  
- **Output:**
  - The updated DataFrame with resolved SMILES values for missing entries.
  - The updated DataFrame is saved as `step4_missing_smiles_added.csv`.

**Execution Time:**
- The progress of fetching ILThermo data for each ID is displayed using a progress bar (`tqdm`).

**Dependencies:**
- `ilthermopy`: Used to fetch ILThermo data.
- `pandas`: For data manipulation.
- `tqdm`: For displaying progress bars.


### Step 3: **get_smiles.py**

This script fetches ILThermo entry data for each unique ID in the dataset, extracting component details such as name, formula, SMILES, molecular weight, and more. The data is then merged with the existing dataset and saved to a CSV file.

**Key Functions:**

1. **`fetch_entry_data`**:
   - Fetches the ILThermo entry data for a given index (`idx`).
   - Extracts component details for both components in the entry and returns them in a list.

2. **`process_batch`**:
   - Processes a batch of IDs by calling `fetch_entry_data` for each ID.
   - Returns a list of fetched data for each batch.

3. **`fetch_unique_data`**:
   - Fetches unique ILThermo data in batches to prevent redundant requests.
   - Uses `ProcessPoolExecutor` for concurrent data fetching with the specified number of workers.
   - Returns the fetched data.

4. **`save_to_csv`**:
   - Saves the updated DataFrame with the extracted data to a CSV file (`step3_smiles_added.csv`).

5. **`get_smiles`**:
   - Extracts unique IDs from the input dataset.
   - Fetches ILThermo data for each unique ID and merges it with the original dataset.
   - Saves the updated DataFrame to a CSV file.
   - Prints the execution time of the script.

**Parameters and Thresholds:**

- **Input:**
  - `df`: The Pandas DataFrame containing the data (`step2_columns_adjusted.csv`).
  
- **Output:**
  - A DataFrame with the extracted SMILES and other component details merged.
  - The updated DataFrame is saved as `step3_smiles_added.csv`.

**Execution Time:**
- The time taken to complete the data extraction is printed at the end of the script.

**Dependencies:**
- `ilthermopy`: Used to fetch ILThermo data.
- `pandas`: For data manipulation.
- `concurrent.futures`: For concurrent processing.
- `tqdm`: For displaying progress bars.


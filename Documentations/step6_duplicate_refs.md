### Step 6: **remove_duplicate_refs.py**

This script processes the dataset to identify and remove rows with duplicate references (`ref`) based on their titles. It ensures that references with the same title are treated as duplicates, even if they have different `ref` values. The removed rows and references are saved to separate files.

**Key Functions:**

1. **`load_csv`**:
   - Loads the dataset from a specified CSV file into a Pandas DataFrame.

2. **`ensure_column_exists`**:
   - Checks whether the specified column exists in the DataFrame. If not, raises a `KeyError`.

3. **`extract_title`**:
   - Extracts the title from a reference string (either in single or double quotes) using regular expressions.

4. **`get_unique_refs`**:
   - Extracts unique reference entries from the dataset and applies the `extract_title` function to each reference to get its title.

5. **`find_duplicate_titles`**:
   - Identifies duplicate titles in the `unique_refs` DataFrame and determines which rows need to be removed based on the title duplication.

6. **`remove_duplicate_refs`**:
   - Removes rows from the original DataFrame that contain duplicate references (based on the title).

7. **`save_to_csv`**:
   - Saves a DataFrame to a CSV file at the specified location.

8. **`duplicate_refs`**:
   - Coordinates the entire process of:
     - Ensuring the presence of the `ref` column.
     - Extracting unique references and their titles.
     - Identifying and removing duplicate references based on their titles.
     - Saving the removed rows, removed references, and the filtered dataset to CSV files.

**Parameters and Thresholds:**

- **Input:**
  - `df`: The Pandas DataFrame containing the dataset (`step5_place_smiles_for_IL_and_solute.csv`).

- **Output:**
  - The updated dataset, with duplicate references removed, is saved as `step6_activity_data_removed_duplicate_refs.csv`.
  - The removed rows are saved as `step6_removed_rows_for_duplicate_refs.csv`.
  - The removed references are saved as `step6_removed_refs_for_duplicate_refs.csv`.

**Execution Time:**
- The processing time depends on the size of the dataset, with outputs being printed after the process completes.

**Dependencies:**
- `pandas`: For data manipulation.
- `re`: For regular expression matching.

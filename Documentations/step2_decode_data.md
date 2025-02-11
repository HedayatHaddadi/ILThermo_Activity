### Step 2: **docode_data.py**

This script processes the raw data from `step1_raw_activity_data.csv`, cleans it, and adjusts columns based on specific conditions. It handles missing values in the 'V4' column, assigns values to new columns (`temperature`, `pressure`, and `mole_fraction`), and performs a sanity check to ensure the adjusted data is consistent.

**Key Functions:**

1. **`docode_data`**:
   - Processes the input DataFrame row by row, handling empty 'V4' values and assigning values to new columns (`temperature`, `pressure`, `mole_fraction`) based on conditions in `V1`, `V2`, and `V3`.
   - Performs a sanity check to ensure the consistency of the adjusted data by comparing the original and new column sums.
   - Saves the adjusted data to a new CSV file and reports any failed rows that did not pass the sanity check.

**Parameters and Thresholds:**

- **Input:**
  - `df`: The Pandas DataFrame to be processed (read from `step1_raw_activity_data.csv`).

- **Columns:**
  - `V1`, `V2`, `V3`, `V4`: Experimental data columns that are used for adjusting and processing values.
  - **New Columns:**
    - `temperature`, `pressure`, `mole_fraction`: These columns are assigned values based on conditions in `V1`, `V2`, and `V3`.
    - `gamma`: Created from the `V4` column.
    - `sum_original`, `sum_new`, `sanity_check`: Used to validate the processed data.

- **Thresholds and Criteria:**
  - **Sanity Check**: Rows where the absolute difference between `sum_original` and `sum_new` is less than `1e-6` are retained. Otherwise, they are flagged.
  - **Solvent Exclusion**: Rows with solvents `water`, `methanol`, `ethanol`, or `propan-1-ol` are removed.
  - **Pressure Assignment**: If a value in `V1`, `V2`, or `V3` is between 98 and 102, it is assigned as the value of `pressure`.
  - **Temperature Assignment**: If a value in `V1`, `V2`, or `V3` is greater than 250, it is assigned as the value of `temperature`.
  - **Mole Fraction Assignment**: If a value in `V1`, `V2`, or `V3` is less than 5, it is assigned as the value of `mole_fraction`.
  - **Mole Fraction Threshold**: Retain rows with a `mole_fraction` less than `1e-5` to represent infinite dilution.

- **Output:**
  - **Returned DataFrame**: The cleaned DataFrame (`df_copy`).
  - **Saved Files**:
    - The processed data is saved to `Intermediate_Data/step2_columns_adjusted.csv`.
    - Failed rows that did not pass the sanity check are saved to `Intermediate_Data/step2_sanity_check_failed_rows_for_column_adjusment.csv`.

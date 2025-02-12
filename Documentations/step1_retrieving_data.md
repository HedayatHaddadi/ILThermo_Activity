### Step 1: **retrieving_data.py**
# Data Retrieval and Processing Script Documentation

## Overview
This script retrieves and processes data from the ILThermo database, handles retries and timeouts, and combines metadata with the retrieved data. The final output is saved as a CSV file.

## Functions

### `process_entry(entry_id, max_retries=3, timeout=10)`
Processes a single entry with retries and timeout handling.

**Parameters:**
- `entry_id`: The unique identifier for the entry to retrieve from ILThermo.
- `max_retries`: The maximum number of retry attempts in case of failure (default is 3).
- `timeout`: Timeout period (in seconds) for the HTTP request (default is 10).

**Returns:**
- A DataFrame combining metadata and data from the ILThermo entry, or `None` if the entry could not be processed after retries.

**Error Handling:**
- Handles timeout (`requests.exceptions.Timeout`), request errors (`requests.exceptions.RequestException`), and other unexpected exceptions. 
- Implements an exponential backoff for retries (e.g., 2s, 4s, 8s).

### `get_and_combine_data(search_params, filename="step1_raw_activity_data.csv", max_workers=None)`
Searches ILThermo, retrieves data (parallelized), combines, and saves to CSV.

**Parameters:**
- `search_params`: A dictionary containing search parameters to query the ILThermo database.
- `filename`: The name of the CSV file to save the combined data (default is `"step1_raw_activity_data.csv"`).
- `max_workers`: The number of parallel workers for processing entries (default is 1).

**Returns:**
- A DataFrame containing the combined data from all retrieved entries.

## Search Parameters, Thresholds, and Criteria

**Parameters:**
- `search_params`: A dictionary containing the search criteria for querying ILThermo.
  - `"prop_key"`: Property key for the desired physical property (e.g., `"BPpY"`).
  - `"n_compounds"`: Number of compounds (default is 2).
  - Additional parameters can be added to refine the search.

**Thresholds:**
- **Retry Logic**: Maximum retries (3), Timeout (10s).
- **Parallelization**: Number of workers controlled by `max_workers` (default 1, set to 4 in main execution).

## File Handling
- The script saves the combined data to `Intermediate_Data/step1_raw_activity_data.csv`.

## Error Handling
- The script retries failed requests up to 3 times with exponential backoff (2s, 4s, 8s).

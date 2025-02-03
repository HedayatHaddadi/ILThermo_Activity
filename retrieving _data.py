import ilthermopy
import pandas as pd
import requests  # For handling timeouts
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

def process_entry(entry_id, max_retries=3, timeout=10):
    """Processes a single entry with retries and timeout handling."""
    for attempt in range(max_retries):
        try:
            entry = ilthermopy.GetEntry(entry_id)  # ilthermopy uses requests internally
            
            if entry is None:
                print(f"Error: Could not retrieve entry with ID {entry_id}")
                return None

            data_df = entry.data
            if data_df is None or data_df.empty:
                print(f"Warning: No data found for entry ID {entry_id}")
                return None

            ref_dict = {}
            if hasattr(entry.ref, '__dict__'):
                ref_dict = entry.ref.__dict__
            elif hasattr(entry.ref, 'to_dict'):
                ref_dict = entry.ref.to_dict()
            else:
                ref_dict = str(entry.ref)

            # Ensure metadata applies to all rows
            metadata = {
                'id': entry_id,
                'ref': ref_dict,
                'phases': entry.phases,
                'expmeth': entry.expmeth,
                'solvent': entry.solvent,
                'property': entry.property,
                'property_type': entry.property_type
            }
            
            metadata_df = pd.DataFrame([metadata] * len(data_df))  # Duplicate metadata for all rows
            combined_df_entry = pd.concat([metadata_df, data_df], axis=1)
            return combined_df_entry
        
        except requests.exceptions.Timeout:
            print(f"Timeout error for entry {entry_id} (attempt {attempt+1}/{max_retries}). Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Request error for entry {entry_id} (attempt {attempt+1}/{max_retries}): {e}")
        except Exception as e:
            print(f"Unexpected error processing entry {entry_id} (attempt {attempt+1}/{max_retries}): {e}")

        # Wait before retrying (exponential backoff: 2s, 4s, 8s)
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
    
    return None  # If all retries fail


def get_and_combine_data(search_params, filename="raw_activity_data.csv", max_workers=None):
    """
    Searches ILThermo, retrieves data (parallelized), combines, and saves to CSV.
    Includes a progress bar and retries for robustness.
    """
    try:
        if not isinstance(search_params, dict):
            raise ValueError("search_params must be a dictionary.")

        if "n_compounds" not in search_params:
            search_params["n_compounds"] = 2  # Ensure a default value

        search_results = ilthermopy.search.Search(**search_params)

        if search_results.empty:
            print("No entries found matching the criteria.")
            return

        entry_ids = [row['id'] for index, row in search_results.iterrows()]
        num_entries = len(entry_ids)

        all_data = []
        if max_workers is None:
            max_workers = 1

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_entry, entry_id) for entry_id in entry_ids]

            with tqdm(total=num_entries, desc="Processing Entries", unit="entry") as pbar:
                for future in as_completed(futures):
                    combined_df_entry = future.result()
                    if combined_df_entry is not None:
                        all_data.append(combined_df_entry)
                    pbar.update(1)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
            print(combined_df[['id', 'ref', 'phases', 'expmeth', 'solvent', 'property', 'property_type']].head())
        else:
            print("No data retrieved or processed.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Define the search parameters dictionary
search_params = {
    "prop_key": "BPpY",  # Modify with correct property key if needed
    "n_compounds": 2
    # Additional parameters can be added here
}

if __name__ == '__main__':
    get_and_combine_data(search_params, max_workers=4)

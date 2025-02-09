import ilthermopy as ilt
import pandas as pd
import time
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# -------------------- Function to Fetch Data --------------------
def fetch_entry_data(idx):
    """Fetch ILThermo entry data and extract component details."""
    try:
        entry = ilt.GetEntry(idx)
        cmp1, cmp2 = entry.components[0], entry.components[1]
        return [
            idx,  # Keep ID for merging
            cmp1.id, cmp1.name, cmp1.formula, cmp1.smiles, cmp1.smiles_error, cmp1.sample, cmp1.mw,
            cmp2.id, cmp2.name, cmp2.formula, cmp2.smiles, cmp2.smiles_error, cmp2.sample, cmp2.mw
        ]
    except Exception:
        return [idx] + [None] * 13  # Fill missing values with None in case of error

# -------------------- Function to Process a Batch --------------------
def process_batch(batch):
    """Process a batch of IDs by fetching their ILThermo data."""
    return [fetch_entry_data(i) for i in batch]

# -------------------- Function to Process Unique IDs --------------------
def fetch_unique_data(unique_ids, batch_size=50, num_workers=10):
    """Fetch only unique data in batches to prevent redundant requests."""
    results = []
    batches = [unique_ids[i:i+batch_size] for i in range(0, len(unique_ids), batch_size)]  # Create batches

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_batch, batch): batch for batch in batches}
        for future in tqdm(futures, total=len(batches), desc="Fetching unique ILThermo data"):
            results.extend(future.result())  # Extend list with results

    return results

# -------------------- Function to Save Data --------------------
def save_to_csv(df, filename="step3_updated_activity_data.csv"):
    """Save DataFrame to CSV file."""
    df.to_csv(filename, index=False)
    print(f"✅ Data extraction complete! Saved as '{filename}'")

# -------------------- Main Function --------------------
def main():
    # Load dataset
    file_path = "step2_processed_activity_data.csv"
    df = pd.read_csv(file_path)

    # Extract unique IDs
    unique_ids = df["id"].unique().tolist()

    # Start time tracking
    start_time = time.time()

    # Fetch only unique ID data
    unique_results = fetch_unique_data(unique_ids)

    # Convert to DataFrame
    columns = [
        "id", "cmp1_id", "cmp1_name", "cmp1_formula", "cmp1_smiles", "cmp1_smiles_error", "cmp1_sample", "cmp1_mw",
        "cmp2_id", "cmp2_name", "cmp2_formula", "cmp2_smiles", "cmp2_smiles_error", "cmp2_sample", "cmp2_mw"
    ]
    unique_df = pd.DataFrame(unique_results, columns=columns)

    # Merge with full dataset (ensuring all rows get their respective component data)
    df = df.merge(unique_df, on="id", how="left")

    # Save updated dataset
    save_to_csv(df)

    # Print execution time
    print(f"⏳ Execution Time: {time.time() - start_time:.2f} seconds")

# -------------------- Run the Script --------------------
if __name__ == "__main__":
    main()

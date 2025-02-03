import ilthermopy as ilt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
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
    except Exception as e:
        return [idx] + [None] * 13  # Fill missing values with None in case of error


# -------------------- Function to Process Data in Parallel --------------------
def fetch_all_data(ids, num_workers=12):
    """Fetch ILThermo data for all IDs using parallel processing."""
    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:  # Process-based parallelism
        futures = {executor.submit(fetch_entry_data, idx): idx for idx in ids}
        for future in tqdm(as_completed(futures), total=len(ids), desc="Fetching ILThermo data"):
            results.append(future.result())
    return results


# -------------------- Function to Save Data --------------------
def save_to_csv(df, filename="updated_activity_data.csv"):
    """Save DataFrame to CSV file."""
    df.to_csv(filename, index=False)
    print(f"✅ Data extraction complete! Saved as '{filename}'")


# -------------------- Main Function --------------------
def main():
    # Load dataset
    file_path = "processed_activity_data.csv"
    df = pd.read_csv(file_path)

    # Fetch data in parallel
    results = fetch_all_data(df.id)

    # Convert to DataFrame
    columns = [
        "id", "cmp1_id", "cmp1_name", "cmp1_formula", "cmp1_smiles", "cmp1_smiles_error", "cmp1_sample", "cmp1_mw",
        "cmp2_id", "cmp2_name", "cmp2_formula", "cmp2_smiles", "cmp2_smiles_error", "cmp2_sample", "cmp2_mw"
    ]
    components_df = pd.DataFrame(results, columns=columns)

    # Merge with original dataset
    df = df.merge(components_df, on="id")

    # Save updated dataset
    save_to_csv(df)


# -------------------- Run the Script --------------------
if __name__ == "__main__":
    main()

import pandas as pd
import ast

# Load the dataset
processed_df = pd.read_csv("processed_with_selected_group.csv")

# Function to extract indices from string representation of lists
def extract_indices(index_str):
    try:
        return ast.literal_eval(index_str) if isinstance(index_str, str) else []
    except:
        return []

# Step 1: Get indices from the selected group column
selected_indices = []
for _, row in processed_df.iterrows():
    group_col = f"original_index_group_{row['selected_group']}"  # Determine the correct column
    if group_col in processed_df.columns:
        selected_indices.extend(extract_indices(row[group_col]))  # Extract and append indices

# Convert to a unique list if needed
selected_indices = list(set(selected_indices))

# Sanity check
print(f"Total selected indices count: {len(selected_indices)}")
print(selected_indices)
import os
import pandas as pd
import re

# Define file path
base_dir = os.getcwd()
file_path = os.path.join(base_dir, 'ref_ids.csv')

# Load CSV file
df = pd.read_csv(file_path, dtype=str)  # Ensure all data is read as strings

# Ensure required columns exist
if 'ref' not in df.columns or 'ref_id' not in df.columns:
    raise KeyError("The CSV file must contain 'ref' and 'ref_id' columns.")

# Extract the title using regex (handles both single and double quotes)
def extract_title(ref_text):
    match = re.search(r"'title':\s*'([^']+)'|\"title\":\s*\"([^\"]+)\"", str(ref_text))
    return match.group(1) if match and match.group(1) else match.group(2) if match else None

# Create the 'title' column
df['title'] = df['ref'].apply(extract_title)

# Identify duplicate titles
duplicate_titles = df[df.duplicated('title', keep=False)]  # Find all duplicate titles
unique_refs = duplicate_titles.drop_duplicates('title', keep='first')  # Keep first ref_id per title

# Remove all occurrences of duplicate titles from the original dataframe
df = df[~df['title'].isin(duplicate_titles['title'])]

# Add back only one ref_id per title
df = pd.concat([df, unique_refs], ignore_index=True)

# Save the updated dataframe
output_file = os.path.join(base_dir, 'updated_ref_ids.csv')
df.drop(columns=['title']).to_csv(output_file, index=False)  # Remove the title column before saving

# Print summary
print(f"Total rows after removing duplicates: {len(df)}")
print(f"Updated ref_ids saved to: {output_file}")

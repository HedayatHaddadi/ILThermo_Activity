import pandas as pd
import ast

# Load datasets
processed_df = pd.read_csv("processed_with_selected_group.csv")
gh_multiple_df = pd.read_csv("gh_filtered_activity_data_multiple.csv")
gh_filtered_df = pd.read_csv("gh_filtered_activity_data.csv")
filtered_activity_df = pd.read_csv("filtered_activity_data.csv")

# Ensure 'selected_group' is treated as an integer, skip if None
processed_df['selected_group'] = processed_df['selected_group'].apply(lambda x: int(x) if pd.notnull(x) else None)

# Get the indices of all selected groups
selected_indices_multiple = []
for index, row in processed_df.iterrows():
    if pd.notnull(row['selected_group']):
        group_column = f"original_index_group_{int(row['selected_group'])}"
        indices = ast.literal_eval(row[group_column])
        selected_indices_multiple.extend(indices)

        # Remove rows present in gh_filtered_activity_data_multiple from gh_filtered_activity_data
        gh_filtered_activity_data_single = gh_filtered_df[~gh_filtered_df.index.isin(gh_multiple_df.index)]

        # Get all indices from 'original_index' column
        original_indices_single = gh_filtered_activity_data_single['original_index'].tolist()


# save gh_filtered_activity_data_single to csv
gh_filtered_activity_data_single.to_csv("gh_filtered_activity_data_single.csv", index=False)

# check if the size of the gh_filtered_activity_data is the same as the sum of the sizes of gh_filtered_activity_data_single and gh_multiple_df
if len(gh_filtered_df) == len(gh_filtered_activity_data_single) + len(gh_multiple_df):
    print("Data size check passed: gh_filtered_df size is equal to the sum of gh_filtered_activity_data_single and gh_multiple_df sizes.")
else:
    print("Data size check failed: gh_filtered_df size is not equal to the sum of gh_filtered_activity_data_single and gh_multiple_df sizes.")


# add sanity check for the sum population column for gh_filtered_df, gh_filtered_activity_data_single and gh_multiple_df
if gh_filtered_df['population'].sum() == gh_filtered_activity_data_single['population'].sum() + gh_multiple_df['population'].sum():
    print("Sanity check passed: population sum of gh_filtered_df is equal to the sum of population of gh_filtered_activity_data_single and gh_multiple_df.")
else:
    print("Sanity check failed: population sum of gh_filtered_df is not equal to the sum of population of gh_filtered_activity_data_single and gh_multiple_df.")

# get the difference between the population sum of gh_filtered_df and the sum of population of gh_filtered_activity_data_single and gh_multiple_df
population_diff = gh_filtered_df['population'].sum() - gh_filtered_activity_data_single['population'].sum() - gh_multiple_df['population'].sum()
print(f"Population difference: {population_diff}")

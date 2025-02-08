import os
import pandas as pd
import numpy as np
import ast
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
import random

# Load dataset
base_dir = os.getcwd()
file_path = os.path.join(base_dir, 'filtered_grouped_data.csv')
processed_df = pd.read_csv(file_path)

# Convert string representation of lists to actual lists
for col in processed_df.columns:
    if col.startswith("inv_temperature_group_") or col.startswith("ln_gamma_group_"):
        processed_df[col] = processed_df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Ensure all values are lists
for col in processed_df.columns:
    if col.startswith("inv_temperature_group_") or col.startswith("ln_gamma_group_"):
        processed_df[col] = processed_df[col].apply(lambda x: [x] if isinstance(x, (int, float)) and not np.isnan(x) else x)

# Custom Chow test function
def chow_test(x1, y1, x2, y2):
    """Perform a Chow test to compare two regressions."""
    x1, y1, x2, y2 = np.array(x1), np.array(y1), np.array(x2), np.array(y2)

    if len(x1) < 2 or len(x2) < 2:  # Ensure enough data points for regression
        return None, None, None

    X1 = sm.add_constant(x1)
    X2 = sm.add_constant(x2)

    model1 = sm.OLS(y1, X1).fit()
    model2 = sm.OLS(y2, X2).fit()

    X_combined = np.concatenate((X1, X2), axis=0)
    y_combined = np.concatenate((y1, y2), axis=0)

    model_combined = sm.OLS(y_combined, X_combined).fit()

    rss_pooled = sum((y_combined - model_combined.predict(X_combined))**2)
    rss1 = sum((y1 - model1.predict(X1))**2)
    rss2 = sum((y2 - model2.predict(X2))**2)

    k = 2  # Intercept & slope
    n1, n2 = len(y1), len(y2)

    if (n1 + n2 - 2 * k) <= 0:  # Prevent invalid F-test
        return None, None, None

    F_stat = ((rss_pooled - (rss1 + rss2)) / k) / ((rss1 + rss2) / (n1 + n2 - 2 * k))
    p_value = 1 - stats.f.cdf(F_stat, k, n1 + n2 - 2 * k)

    significant = p_value < 0.05

    return F_stat, p_value, significant

# Define all possible 21 combinations
group_combinations = list(combinations(range(7), 2))

# Initialize new columns with NaN
for g1, g2 in group_combinations:
    processed_df[f"F_group_{g1}_{g2}"] = np.nan
    processed_df[f"p_group_{g1}_{g2}"] = np.nan
    processed_df[f"s_group_{g1}_{g2}"] = np.nan

# Apply Chow test
for index, row in processed_df.iterrows():
    for g1, g2 in group_combinations:
        x1, y1 = row.get(f"inv_temperature_group_{g1}"), row.get(f"ln_gamma_group_{g1}")
        x2, y2 = row.get(f"inv_temperature_group_{g2}"), row.get(f"ln_gamma_group_{g2}")

        if not isinstance(x1, list) or not isinstance(y1, list) or not isinstance(x2, list) or not isinstance(y2, list):
            continue  # Skip if either group is missing

        if len(x1) != len(y1) or len(x2) != len(y2):
            continue  # Skip if data sizes are mismatched

        F_stat, p_value, significant = chow_test(x1, y1, x2, y2)
        processed_df.loc[index, f"F_group_{g1}_{g2}"] = F_stat
        processed_df.loc[index, f"p_group_{g1}_{g2}"] = p_value
        processed_df.loc[index, f"s_group_{g1}_{g2}"] = float(significant)  # Explicitly cast to float




# Count the number of times each group contributes to 0 values in s_group_ columns
for g in range(7):
    processed_df[f"False_count_group_{g}"] = 0

for index, row in processed_df.iterrows():
    false_counts = {g: 0 for g in range(7)}
    for g1, g2 in group_combinations:
        if row[f"s_group_{g1}_{g2}"] == 0:
            false_counts[g1] += 1
            false_counts[g2] += 1
    for g in range(7):
        processed_df.at[index, f"False_count_group_{g}"] = false_counts[g]




# Function to get the max gamma and number of samples for a group
def get_group_stats(row, group):
    gamma_values = row[f"ln_gamma_group_{group}"]
    if isinstance(gamma_values, list):
        max_gamma = max(gamma_values)
        num_samples = len(gamma_values)
    else:
        max_gamma = None
        num_samples = 0
    return max_gamma, num_samples

# Function to get the R2 value for a group
def get_group_r2(row, group):
    return row.get(f"r2_group_{group}", None)

# Determine the selected group for each row
selected_groups = []
for index, row in processed_df.iterrows():
    false_counts = {g: row[f"False_count_group_{g}"] for g in range(7)}
    max_false_count = max(false_counts.values())

    if max_false_count == 0:
        if row["r2_general_group"] > 0.9:
            r2_columns = [col for col in processed_df.columns if col.startswith("r2_group_")]
            non_null_r2_columns = [col for col in r2_columns if pd.notnull(row[col])]
            if len(non_null_r2_columns) == 1:
                selected_groups.append(int(non_null_r2_columns[0].split("_")[-1]))
                continue
            r2_values = {g: get_group_r2(row, g) for g in range(7)}
            max_r2 = max(r2_values.values())
            candidates = [g for g, r2 in r2_values.items() if r2 == max_r2]
            if len(candidates) == 1:
                selected_groups.append(candidates[0])
                continue
            gamma_values = {g: get_group_stats(row, g)[0] for g in candidates}
            if gamma_values:
                max_gamma = max(gamma_values.values())
                candidates = [g for g, gamma in gamma_values.items() if gamma == max_gamma]
                if len(candidates) == 1:
                    selected_groups.append(candidates[0])
                    continue
            else:
                selected_groups.append(None)
                continue
            sample_counts = {g: get_group_stats(row, g)[1] for g in candidates}
            max_samples = max(sample_counts.values())
            candidates = [g for g, samples in sample_counts.items() if samples == max_samples]
            selected_groups.append(random.choice(candidates))
        else:
            selected_groups.append(None)
    else:
        candidates = [g for g, count in false_counts.items() if count == max_false_count]
        if len(candidates) == 1:
            selected_groups.append(candidates[0])
            continue
        r2_values = {g: get_group_r2(row, g) for g in candidates}
        max_r2 = max(r2_values.values())
        candidates = [g for g, r2 in r2_values.items() if r2 == max_r2]
        if len(candidates) == 1:
            selected_groups.append(candidates[0])
            continue
        gamma_values = {g: get_group_stats(row, g)[0] for g in candidates}
        max_gamma = max(gamma_values.values())
        candidates = [g for g, gamma in gamma_values.items() if gamma == max_gamma]
        if len(candidates) == 1:
            selected_groups.append(candidates[0])
            continue
        sample_counts = {g: get_group_stats(row, g)[1] for g in candidates}
        max_samples = max(sample_counts.values())
        candidates = [g for g, samples in sample_counts.items() if samples == max_samples]
        selected_groups.append(random.choice(candidates))

# Add the selected group column to the DataFrame
processed_df["selected_group"] = selected_groups

# Save the updated DataFrame
output_path = os.path.join(base_dir, 'processed_with_selected_group.csv')
processed_df.to_csv(output_path, index=False)

import os
import pandas as pd
import numpy as np
import ast
import statsmodels.api as sm
from scipy import stats
from itertools import combinations

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

# Save results
output_path = os.path.join(base_dir, 'processed_with_chow_test.csv')
processed_df.to_csv(output_path, index=False)

# Print sample output
print("\nSample of updated DataFrame with Chow test results:")

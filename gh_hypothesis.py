import numpy as np
import pandas as pd
import scipy.stats as stats

# Step 1: Load the CSV files
step8_df = pd.read_csv("Intermediate_Data/step8_gh_single_ref_combinations.csv")
step9_df = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved.csv")

# Step 2: Extract r_squared values from step8
r_squared_step8 = step8_df['r_squared'].dropna().tolist()  # drop NaN values and convert to list

# Step 3: Extract r2_group_* columns from step9
# First, select columns starting with 'r2_group_'
r2_group_columns = [col for col in step9_df.columns if col.startswith('r2_group_')]

# Extract values from those columns, drop NaN values, and flatten the result into a list
r_squared_step9 = step9_df[r2_group_columns].stack().dropna().tolist()

# Step 4: Combine both lists
combined_r_squared = np.array(r_squared_step8 + r_squared_step9)

# remove values less than 0.05 since they may be temperature insensitive
combined_r_squared = combined_r_squared[combined_r_squared > 0.05]

# calculate mean, median, and standard deviation
mean = np.mean(combined_r_squared)
median = np.median(combined_r_squared)
std_dev = np.std(combined_r_squared)
print(f"Mean: {mean:.4f}, Median: {median:.4f}, Standard Deviation: {std_dev:.4f}")

# Step 5: Calculate proportion of samples with R^2 > 0.9
proportion_above_0_9 = np.sum(combined_r_squared > 0.9) / len(combined_r_squared)
print(f"Proportion of mixtures with R^2 > 0.9: {proportion_above_0_9:.4f}")

# Step 6: Perform a Chi-Square test for proportions
# We expect 90% (0.9) of samples to have R^2 > 0.9, so the expected count is 0.9 * len(combined_r_squared)
expected_proportion = 0.9
observed_count = np.sum(combined_r_squared > 0.9)
expected_count = expected_proportion * len(combined_r_squared)

# Calculate the test statistic and p-value for Chi-Square test for proportions
observed = np.array([observed_count, len(combined_r_squared) - observed_count])
expected = np.array([expected_count, len(combined_r_squared) - expected_count])
chi2_stat, p_value_chi2 = stats.chisquare(observed, expected)

print(f"Chi-Square test p-value: {p_value_chi2}")
if p_value_chi2 < 0.05:
    print("Reject the null hypothesis: The proportion of mixtures with R^2 > 0.9 is significantly different from 90%.")
else:
    print("Fail to reject the null hypothesis: The proportion of mixtures with R^2 > 0.9 is not significantly different from 90%.")

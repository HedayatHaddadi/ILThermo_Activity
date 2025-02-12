import numpy as np
import pandas as pd
# import scipy.stats as stats

# Step 1: Load the CSV files
step8_df = pd.read_csv("Intermediate_Data/step8_gh_single_ref_combinations.csv")
step9_df = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved.csv")

# Step 2: Extract r_squared values from step8
r_squared_step8 = step8_df['r_squared'].dropna().tolist()  # drop NaN values and convert to list
# extract corresponding number of samples in step8_df from population column for each r_squared value
population_step8 = step8_df['population'].dropna().tolist()

# build a dataframe from the extracted values
df_step8 = pd.DataFrame({'r_squared': r_squared_step8, 'population': population_step8})
# shape of the dataframe
print(df_step8.shape)
# print the first 5 rows of the dataframe
print(df_step8.head())


# F-test based adjusted r_squared values
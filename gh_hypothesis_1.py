import numpy as np
import pandas as pd
import os


single_df = pd.read_csv("Intermediate_Data/step8_single_ref_single_entry.csv")
multi_resolved_df = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
single_resolved_df = pd.read_csv("Intermediate_Data/step9_conflicted_data_resolved_single.csv")

r_squared_single_df = single_df['r_squared'].dropna().tolist()  # drop NaN values and convert to list
num_sample_single_df = single_df['population'].dropna().tolist()
r2_single_df = pd.DataFrame({'r_squared': r_squared_single_df, 'population': num_sample_single_df})


def extract_r2_population(df):
    r_squared_list = []
    population_list = []
    
    for _, row in df.iterrows():
        if pd.notna(row['selected_group']):
            selected_group = int(row['selected_group'])
            
            # Extract r_squared value
            r2_col = f'r2_group_{selected_group}'
            r_squared = row[r2_col] if pd.notna(row[r2_col]) else np.nan
            
            # Extract population size
            gamma_col = f'ln_gamma_group_{selected_group}'
            if pd.notna(row[gamma_col]):
                population = len(eval(row[gamma_col]))  # Convert string list to actual list and get length
            else:
                population = np.nan
            
            r_squared_list.append(r_squared)
            population_list.append(population)
    
    return pd.DataFrame({'r_squared': r_squared_list, 'population': population_list})

r2_multi_resolved_df = extract_r2_population(multi_resolved_df)
r2_single_resolved_df = extract_r2_population(single_resolved_df)


if not os.path.exists("stat_analysis"):
    os.makedirs("stat_analysis")
    
r2_all = pd.concat([r2_single_df, r2_multi_resolved_df, r2_single_resolved_df])
r2_all.to_csv("stat_analysis/r2_population.csv", index=False)
assert len(r2_all) == len(r2_single_df) + len(r2_multi_resolved_df) + len(r2_single_resolved_df), "Length of concatenated dataframe is not equal to the sum of the lengths of the individual dataframes"




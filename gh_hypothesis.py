import numpy as np
import pandas as pd
import os

def load_data(file_path):
    return pd.read_csv(file_path)

def prepare_single_df(single_df):
    r_squared_single_df = single_df['r_squared'].dropna().tolist()
    num_sample_single_df = single_df['population'].dropna().tolist()
    return pd.DataFrame({'r_squared': r_squared_single_df, 'population': num_sample_single_df})

def extract_r2_population(df):
    r_squared_list = []
    population_list = []
    num_groups = len([col for col in df.columns if col.startswith("r2_group_")])
    
    for _, row in df.iterrows():
        if pd.notna(row['selected_group']):
            selected_group = int(row['selected_group'])
            
            if selected_group == num_groups - 1:
                continue
            
            r2_col = f'r2_group_{selected_group}'
            r_squared = row[r2_col] if pd.notna(row[r2_col]) else np.nan
            
            gamma_col = f'ln_gamma_group_{selected_group}'
            if pd.notna(row[gamma_col]):
                population = len(eval(row[gamma_col]))
            else:
                population = np.nan
            
            r_squared_list.append(r_squared)
            population_list.append(population)
    
    return pd.DataFrame({'r_squared': r_squared_list, 'population': population_list})

def save_results(df, directory="stat_analysis"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    df.to_csv(os.path.join(directory, "r2_all.csv"), index=False)

def main():
    single_df = load_data("Intermediate_Data/step8_single_ref_single_entry.csv")
    multi_resolved_df = load_data("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
    single_resolved_df = load_data("Intermediate_Data/step9_conflicted_data_resolved_single.csv")

    r2_single_df = prepare_single_df(single_df)
    r2_multi_resolved_df = extract_r2_population(multi_resolved_df)
    r2_single_resolved_df = extract_r2_population(single_resolved_df)

    r2_all = pd.concat([r2_single_df, r2_multi_resolved_df, r2_single_resolved_df])
    assert len(r2_all) == len(r2_single_df) + len(r2_multi_resolved_df) + len(r2_single_resolved_df), "Length of concatenated dataframe is not equal to the sum of the lengths of the individual dataframes"

    r2_all['f_test'] = (r2_all['r_squared'] / (1 - r2_all['r_squared'])) * (r2_all['population'] - 2)

    num_pass_f_test = len(r2_all[r2_all['f_test'] > 3.84])
    percentage_pass_f_test = num_pass_f_test / len(r2_all) * 100
    print(f"Percentage of entries passing the F test: {percentage_pass_f_test:.0f}%")
    print(f"Mean R^2: {r2_all['r_squared'].mean():.4f}")
    print(f"Standard Deviation of R^2: {r2_all['r_squared'].std():.4f}")

    save_results(r2_all)

if __name__ == "__main__":
    main()

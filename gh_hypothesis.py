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

def save_results(df, name, directory="stat_analysis"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    df.to_csv(os.path.join(directory, f"r2_all_{name}.csv"), index=False)

def gh_ftest():
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
    mean_r2 = r2_all['r_squared'].mean()
    std_r2 = r2_all['r_squared'].std()

    results = [
        f"Percentage of entries passing the F test: {percentage_pass_f_test:.0f}%",
        f"Mean R^2: {mean_r2:.4f}",
        f"Standard Deviation of R^2: {std_r2:.4f}"
    ]

    save_results(r2_all, 'total')

    r2_all_filtered = r2_all[r2_all['r_squared'] >= 0.01] # to exclude temperature insensitive entries

    num_pass_f_test_filtered = len(r2_all_filtered[r2_all_filtered['f_test'] > 3.84])
    percentage_pass_f_test_filtered = num_pass_f_test_filtered / len(r2_all_filtered) * 100
    mean_r2_filtered = r2_all_filtered['r_squared'].mean()
    std_r2_filtered = r2_all_filtered['r_squared'].std()

    results.extend([
        f"Percentage of entries passing the F test (filtered): {percentage_pass_f_test_filtered:.0f}%",
        f"Mean R^2 (filtered): {mean_r2_filtered:.4f}",
        f"Standard Deviation of R^2 (filtered): {std_r2_filtered:.4f}"
    ])

    save_results(r2_all_filtered, 'filtered')

    with open(os.path.join("stat_analysis", "ftest_results.txt"), "w") as f:
        for line in results:
            f.write(line + "\n")



def calculate_percentage(df, selected_group_col, false_count_group_col):
    """Calculate the percentage of entries that passed the Chow test."""
    not_none_count = df[selected_group_col].notna().sum()
    total_count = len(df[false_count_group_col])
    percentage_passed = (not_none_count / total_count) * 100
    return percentage_passed

def chow_pass():
    # Load dataframes
    multi_resolved_df = load_data("Intermediate_Data/step9_conflicted_data_resolved_multi.csv")
    single_resolved_df = load_data("Intermediate_Data/step9_conflicted_data_resolved_single.csv")

    # Calculate percentages
    multi_ref_percentage = calculate_percentage(multi_resolved_df, 'selected_group', 'False_count_group_0')
    single_ref_percentage = calculate_percentage(single_resolved_df, 'selected_group', 'False_count_group_0')

    # Prepare results
    results = (
        f"Percentage of entries passed the Chow test in multi_ref: {multi_ref_percentage:.2f}%\n"
        f"Percentage of entries passed the Chow test in single_ref: {single_ref_percentage:.2f}%\n"
    )

    # Save results to file
    with open("stat_analysis/chow_test_passed.txt", "w") as file:
        file.write(results)


if __name__ == "__main__":
    gh_ftest()
    chow_pass()

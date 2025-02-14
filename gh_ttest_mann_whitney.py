import numpy as np
import pandas as pd
import scipy.stats as stats

def load_data(file_path):
    return pd.read_csv(file_path)

def extract_r_squared(dataframe):
    return dataframe['r_squared']

def perform_ttest(group1, group2):
    return stats.ttest_ind(group1, group2)

def perform_mannwhitneyu(group1, group2):
    return stats.mannwhitneyu(group1, group2)

def write_results(file, test_name, result, group1_name, group2_name):
    file.write(f"{test_name} between {group1_name} and {group2_name}: {result}\n")
    if result.pvalue < 0.05:
        file.write(f"The difference between {group1_name} and {group2_name} is significant.\n")
    else:
        file.write(f"The difference between {group1_name} and {group2_name} is not significant.\n")

def ttest_mann_whitney():
    # Step 1: Load the CSV files
    single_ref_single_entry = load_data("Intermediate_Data/step8_single_ref_single_entry.csv")
    single_ref_multi_entry = load_data("Intermediate_Data/step8_single_ref_multiple_entry.csv")
    multi_ref = load_data("Intermediate_Data/step8_gh_multiple_ref_combinations.csv")

    # Step 2: Extract the r_squared columns
    r_squared_single_ref_single_entry = extract_r_squared(single_ref_single_entry)
    r_squared_single_ref_multi_entry = extract_r_squared(single_ref_multi_entry)
    r_squared_multi_ref = extract_r_squared(multi_ref)

    # Step 3: Perform t-tests
    ttest_single_vs_multi_entry = perform_ttest(r_squared_single_ref_single_entry, r_squared_single_ref_multi_entry)
    ttest_single_vs_multi_ref = perform_ttest(r_squared_single_ref_single_entry, r_squared_multi_ref)
    ttest_multi_entry_vs_multi_ref = perform_ttest(r_squared_single_ref_multi_entry, r_squared_multi_ref)

    # Step 4: Perform Mann-Whitney U tests
    mannwhitney_single_vs_multi_entry = perform_mannwhitneyu(r_squared_single_ref_single_entry, r_squared_single_ref_multi_entry)
    mannwhitney_single_vs_multi_ref = perform_mannwhitneyu(r_squared_single_ref_single_entry, r_squared_multi_ref)
    mannwhitney_multi_entry_vs_multi_ref = perform_mannwhitneyu(r_squared_single_ref_multi_entry, r_squared_multi_ref)

    # Step 5: Print the results
    with open("stat_analysis/ttest_mann-whitney_u_test_results.txt", "w") as file:
        write_results(file, "T-test", ttest_single_vs_multi_entry, "single_ref_single_entry", "single_ref_multi_entry")
        write_results(file, "T-test", ttest_single_vs_multi_ref, "single_ref_single_entry", "multi_ref")
        write_results(file, "T-test", ttest_multi_entry_vs_multi_ref, "single_ref_multi_entry", "multi_ref")

        file.write("\n")
        
        write_results(file, "Mann-Whitney U test", mannwhitney_single_vs_multi_entry, "single_ref_single_entry", "single_ref_multi_entry")
        write_results(file, "Mann-Whitney U test", mannwhitney_single_vs_multi_ref, "single_ref_single_entry", "multi_ref")
        write_results(file, "Mann-Whitney U test", mannwhitney_multi_entry_vs_multi_ref, "single_ref_multi_entry", "multi_ref")

if __name__ == "__main__":
    ttest_mann_whitney()

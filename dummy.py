import os
import json
import pandas as pd
import numpy as np
from scipy import stats
import csv
from itertools import combinations

# Function to perform linear regression and calculate R2
def calculate_regression(inv_temperature, log_gamma):
    slope, intercept, r_value, _, _ = stats.linregress(inv_temperature, log_gamma)
    r_squared = r_value ** 2
    return slope, intercept, r_squared

# Function to perform t-test for comparing two sets of values
def perform_ttest(values1, values2):
    t_stat, p_value = stats.ttest_ind(values1, values2)
    return p_value < 0.05  # If p-value < 0.05, we consider the difference significant

# Function to select the best group and classify selected and rejected samples
def select_best_group_and_classify(row_results, group_data, ref_id_counts):
    selected_samples = []
    rejected_samples = []
    
    # Identify the best group for the row based on the criteria
    best_group = None
    best_group_false_count = -1
    best_group_R2 = -1
    best_group_gamma_range = -1
    best_group_sample_count = -1
    
    for group, data in group_data.items():
        # Count False values for slope and intercept comparisons
        false_count = sum([not ttest['slope_diff'] and not ttest['intercept_diff'] for ttest in row_results['ttest_results'][group].values()])
        
        # Calculate R2, gamma range, and sample count
        R2 = row_results['regression_results'][group]['R2']
        gamma_range = np.ptp(data['log_gamma'])  # Range of gamma values
        sample_count = len(data['log_gamma'])
        
        # Determine the best group based on the outlined rules
        if (false_count > best_group_false_count or
            (false_count == best_group_false_count and R2 > best_group_R2) or
            (false_count == best_group_false_count and R2 == best_group_R2 and gamma_range > best_group_gamma_range) or
            (false_count == best_group_false_count and R2 == best_group_R2 and gamma_range == best_group_gamma_range and sample_count > best_group_sample_count)):
            best_group = group
            best_group_false_count = false_count
            best_group_R2 = R2
            best_group_gamma_range = gamma_range
            best_group_sample_count = sample_count
    
    # Classify selected and rejected samples based on the best group
    for group, data in group_data.items():
        if group == best_group:
            selected_samples.extend(data['original_index'])
        else:
            rejected_samples.extend(data['original_index'])
    
    return selected_samples, rejected_samples

# Function to process the DataFrame and save the result
def process_and_save_selection(df, output_filename='selection_results.csv'):
    selection_data = []

    # Count the number of samples for each ref_id in the dataset
    ref_id_counts = {}
    for _, row in df.iterrows():
        ref_id_list = json.loads(row['ref_id'])
        for ref_id in ref_id_list:
            if ref_id not in ref_id_counts:
                ref_id_counts[ref_id] = 0
            ref_id_counts[ref_id] += 1

    # Iterate over each row and process it
    for _, row in df.iterrows():
        # Convert the required columns from string to lists
        ref_id_list = json.loads(row['ref_id'])
        original_index_list = json.loads(row['original_index'])
        temperature_list = json.loads(row['temperature'])
        gamma_list = json.loads(row['gamma'])

        # Prepare lists for storing natural log of gamma and inverse of temperature
        log_gamma = []
        inv_temperature = []
        group_data = {}
        
        # Collect data for each ref_id (group-wise) and general group
        for ref_id, original_index, temperature, gamma in zip(ref_id_list, original_index_list, temperature_list, gamma_list):
            log_gamma.append(np.log(gamma))
            inv_temperature.append(1/temperature)
            
            # Determine the group for each ref_id
            sample_count = ref_id_counts[ref_id]
            if sample_count >= 3:
                group = f"group_{sample_count}"
            else:
                group = 'seudo_group'
            
            # Append data for group-wise regression
            if group not in group_data:
                group_data[group] = {'log_gamma': [], 'inv_temperature': [], 'original_index': []}
            group_data[group]['log_gamma'].append(np.log(gamma))
            group_data[group]['inv_temperature'].append(1/temperature)
            group_data[group]['original_index'].append(original_index)
        
        # Perform regression and t-test comparisons for the row
        row_results = {
            'regression_results': {},
            'ttest_results': {}
        }
        
        for group, data in group_data.items():
            slope, intercept, r_squared = calculate_regression(data['inv_temperature'], data['log_gamma'])
            row_results['regression_results'][group] = {'slope': slope, 'intercept': intercept, 'R2': r_squared}
        
        # Perform regression for the general group (all data for the row)
        slope, intercept, r_squared = calculate_regression(inv_temperature, log_gamma)
        row_results['regression_results']['general_group'] = {'slope': slope, 'intercept': intercept, 'R2': r_squared}
        
        # Perform pairwise t-test comparisons between all groups and general_group
        for (group1, group2) in combinations(row_results['regression_results'].keys(), 2):
            slope_diff = perform_ttest([row_results['regression_results'][group1]['slope']], [row_results['regression_results'][group2]['slope']])
            intercept_diff = perform_ttest([row_results['regression_results'][group1]['intercept']], [row_results['regression_results'][group2]['intercept']])
            row_results['ttest_results'].setdefault(group1, {})[group2] = {'slope_diff': slope_diff, 'intercept_diff': intercept_diff}
            row_results['ttest_results'].setdefault(group2, {})[group1] = {'slope_diff': slope_diff, 'intercept_diff': intercept_diff}
        
        # Select the best group and classify the samples
        selected_samples, rejected_samples = select_best_group_and_classify(row_results, group_data, ref_id_counts)

        # Add the results to the selection_data list
        selection_data.append({
            'original_index': row['original_index'],
            'selected_samples': selected_samples,
            'rejected_samples': rejected_samples
        })

    # Save the selected and rejected samples as CSV
    with open(output_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['original_index', 'selected_samples', 'rejected_samples'])
        writer.writeheader()
        for row in selection_data:
            writer.writerow(row)

# Apply the function to process the DataFrame and save results
df = pd.read_csv('gh_filtered_activity_data_multiple.csv')  # Assuming the CSV is already loaded
process_and_save_selection(df)

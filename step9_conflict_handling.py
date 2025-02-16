import os
import json
import pandas as pd
from collections import defaultdict
from scipy.stats import linregress
import numpy as np
import ast
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
import random


threshold = 5

def load_dataset(file_path):
    return pd.read_csv(file_path)

def process_row(row):
    def safe_json_loads(value):
        """Ensure json.loads is only applied to string values."""
        return json.loads(value) if isinstance(value, str) else value

    # Apply safe_json_loads to each relevant column
    ref_ids = safe_json_loads(row['ref_id'])
    original_indices = safe_json_loads(row['original_index'])
    temperatures = safe_json_loads(row['temperature'])
    gammas = safe_json_loads(row['gamma'])
    
    ref_counts = {rid: ref_ids.count(rid) for rid in set(ref_ids)}
    groups = defaultdict(lambda: {'ref_id': [], 'original_index': [], 'temperature': [], 'gamma': []})
    
    groups['general_group'] = {
        'ref_id': ref_ids,
        'original_index': original_indices,
        'temperature': temperatures,
        'gamma': gammas
    }
    
    group_idx = 0
    has_sedu_group = False
    for rid, count in ref_counts.items():
        group_name = f'group_{group_idx}' if count >= threshold else 'pseudo_group'
        if count >= threshold:
            group_idx += 1
        else:
            has_sedu_group = True
        
        for i, rid_val in enumerate(ref_ids):
            if rid_val == rid:
                groups[group_name]['ref_id'].append(rid_val)
                groups[group_name]['original_index'].append(original_indices[i])
                groups[group_name]['temperature'].append(temperatures[i])
                groups[group_name]['gamma'].append(gammas[i])
    
    if has_sedu_group:
        groups['pseudo_group'] = {'ref_id': [], 'original_index': [], 'temperature': [], 'gamma': []}
        for rid, count in ref_counts.items():
            if count < threshold:
                for i, rid_val in enumerate(ref_ids):
                    if rid_val == rid:
                        groups['pseudo_group']['ref_id'].append(rid_val)
                        groups['pseudo_group']['original_index'].append(original_indices[i])
                        groups['pseudo_group']['temperature'].append(temperatures[i])
                        groups['pseudo_group']['gamma'].append(gammas[i])
    
    return groups

def calculate_regression(data):
    temperatures = np.array(data['temperature'])
    gammas = np.array(data['gamma'])
    
    if np.any(temperatures == 0):
        return None, None, None
    
    x = 1 / temperatures
    y = np.log(gammas)
    
    slope, intercept, r_value, _, _ = linregress(x, y)
    return slope, intercept, r_value**2

def process_data(df):
    processed_data = []
    failed_rows = []
    for _, row in df.iterrows():
        row_groups = process_row(row)
        general_count = len(row_groups['general_group']['ref_id'])
        other_count = sum(len(data['ref_id']) for group, data in row_groups.items() if group != 'general_group')
        
        if general_count != other_count:
            failed_rows.append(row)
        else:
            processed_data.append(row_groups)
    
    return processed_data, failed_rows

def expand_rows(processed_data):
    expanded_rows = []
    for row_groups in processed_data:
        row_dict = {}
        for group_name, data in row_groups.items():
            for key, values in data.items():
                row_dict[f'{key}_{group_name}'] = json.dumps(values) if key not in ['slope', 'intercept', 'r2'] else values
        expanded_rows.append(row_dict)
    return expanded_rows

def save_failed_rows(failed_rows, name):
    if failed_rows:
        failed_df = pd.DataFrame(failed_rows)
        failed_file = f'Intermediate_Data/step9_failed_rows_while_generating_groups_{name}.csv'
        failed_df.to_csv(failed_file, index=False)
        print(f'Failed rows saved to {failed_file}')
        print('Sanity check failed.')
    else:
        print('Sanity check passed.')

def add_regression_results(processed_data):
    for row_groups in processed_data:
        for group_name, data in row_groups.items():
            if group_name == 'pseudo_group' and len(data['ref_id']) < threshold:
                slope, intercept, r2 = None, None, None
            else:
                slope, intercept, r2 = calculate_regression(data)
            row_groups[group_name]['slope'] = slope
            row_groups[group_name]['intercept'] = intercept
            row_groups[group_name]['r2'] = r2

def save_processed_data(expanded_rows, name):
    processed_df = pd.DataFrame(expanded_rows)
    output_file = f'Intermediate_Data/step9_regression_params_added_{name}.csv'
    processed_df.to_csv(output_file, index=False)
    print(f'Processed data with regression results saved to {output_file}')
    return processed_df

def filter_columns(processed_df):
    group_columns = [col for col in processed_df.columns if 'ref_id_group_' in col]
    group_columns.append('ref_id_pseudo_group')
    group_columns.extend([col for col in processed_df.columns if 'original_index_group_' in col])
    group_columns.append('original_index_pseudo_group')
    group_columns.extend([col for col in processed_df.columns if 'temperature_group_' in col])
    group_columns.append('temperature_pseudo_group')
    group_columns.extend([col for col in processed_df.columns if 'gamma_group_' in col])
    group_columns.append('gamma_pseudo_group')
    group_columns.extend([col for col in processed_df.columns if 'r2_' in col])
    return processed_df[group_columns]

def calculate_ln_and_inv(processed_df):
    for col in processed_df.columns:
        if 'gamma_group_' in col or col == 'gamma_pseudo_group':
            processed_df[f'ln_{col}'] = processed_df[col].apply(lambda x: [np.log(float(i)) for i in json.loads(x)] if isinstance(x, str) else x)
        if 'temperature_group_' in col or col == 'temperature_pseudo_group':
            processed_df[f'inv_{col}'] = processed_df[col].apply(lambda x: [1/float(i) for i in json.loads(x)] if isinstance(x, str) else x)
    return processed_df

def rename_pseudo_group(processed_df):
    group_numbers = [int(col.split('_')[-1]) for col in processed_df.columns if col.split('_')[-1].isdigit()]
    last_group_number = max(group_numbers) if group_numbers else 0
    for col in processed_df.columns:
        if 'pseudo_group' in col:
            new_col_name = col.replace('pseudo_group', f'group_{last_group_number + 1}')
            processed_df.rename(columns={col: new_col_name}, inplace=True)
    return processed_df

def save_filtered_data(processed_df, name):
    output_file = f'Intermediate_Data/step9_filtered_grouped_data_{name}.csv'
    processed_df.to_csv(output_file, index=False)
    print('Filtered DataFrame saved to step9_filtered_grouped_data.csv')

def convert_str_to_list(processed_df):
    for col in processed_df.columns:
        if col.startswith("inv_temperature_group_") or col.startswith("ln_gamma_group_"):
            processed_df[col] = processed_df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    return processed_df

def ensure_list_values(processed_df):
    for col in processed_df.columns:
        if col.startswith("inv_temperature_group_") or col.startswith("ln_gamma_group_"):
            processed_df[col] = processed_df[col].apply(lambda x: [x] if isinstance(x, (int, float)) and not np.isnan(x) else x)
    return processed_df

def chow_test(x1, y1, x2, y2):
    x1, y1, x2, y2 = np.array(x1), np.array(y1), np.array(x2), np.array(y2)

    if len(x1) < threshold or len(x2) < threshold:
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

    k = 2
    n1, n2 = len(y1), len(y2)

    if (n1 + n2 - 2 * k) <= 0:
        return None, None, None

    F_stat = ((rss_pooled - (rss1 + rss2)) / k) / ((rss1 + rss2) / (n1 + n2 - 2 * k))
    p_value = 1 - stats.f.cdf(F_stat, k, n1 + n2 - 2 * k)

    significant = p_value < 0.05

    return F_stat, p_value, significant



def apply_chow_test(processed_df):
    num_groups = len([col for col in processed_df.columns if col.startswith("r2_group_")])
    group_combinations = list(combinations(range(num_groups), 2))

    for g1, g2 in group_combinations:
        processed_df[f"F_group_{g1}_{g2}"] = np.nan
        processed_df[f"p_group_{g1}_{g2}"] = np.nan
        processed_df[f"s_group_{g1}_{g2}"] = np.nan

    for index, row in processed_df.iterrows():
        for g1, g2 in group_combinations:
            x1, y1 = row.get(f"inv_temperature_group_{g1}"), row.get(f"ln_gamma_group_{g1}")
            x2, y2 = row.get(f"inv_temperature_group_{g2}"), row.get(f"ln_gamma_group_{g2}")

            if not isinstance(x1, list) or not isinstance(y1, list) or not isinstance(x2, list) or not isinstance(y2, list) or len(x1) < threshold or len(y1) < threshold or len(x2) < threshold or len(y2) < threshold:
                continue

            if len(x1) != len(y1) or len(x2) != len(y2):
                continue

            F_stat, p_value, significant = chow_test(x1, y1, x2, y2)
            processed_df.loc[index, f"F_group_{g1}_{g2}"] = F_stat
            processed_df.loc[index, f"p_group_{g1}_{g2}"] = p_value
            processed_df.loc[index, f"s_group_{g1}_{g2}"] = float(significant)

    return processed_df

def count_false_contributions(processed_df):
    num_groups = len([col for col in processed_df.columns if col.startswith("r2_group_")])
    for g in range(num_groups):
        processed_df[f"False_count_group_{g}"] = 0

    for index, row in processed_df.iterrows():
        false_counts = {g: 0 for g in range(num_groups)}
        for g1, g2 in list(combinations(range(num_groups), 2)):
            if row[f"s_group_{g1}_{g2}"] == 0:
                false_counts[g1] += 1
                false_counts[g2] += 1
        for g in range(num_groups):
            processed_df.at[index, f"False_count_group_{g}"] = false_counts[g]

    return processed_df

def get_group_stats(row, group):
    gamma_values = row[f"ln_gamma_group_{group}"]
    if isinstance(gamma_values, list):
        max_gamma = max(gamma_values)
        num_samples = len(gamma_values)
    else:
        max_gamma = None
        num_samples = 0
    return max_gamma, num_samples

def get_group_r2_adjusted(row, group):
    r2 = row.get(f"r2_group_{group}", None)
    _, num_samples = get_group_stats(row, group)
    if r2 is not None and num_samples > 1:
        adjusted_r2 = 1 - (1 - r2) * (num_samples - 1) / (num_samples - 2)
        return adjusted_r2
    return None

def determine_selected_group(processed_df):
    selected_groups = []
    
    for index, row in processed_df.iterrows():
        num_groups = len([col for col in processed_df.columns if col.startswith("r2_group_")])
        false_counts = {g: row[f"False_count_group_{g}"] for g in range(num_groups)}
        max_false_count = max(false_counts.values())

        if max_false_count == 0:
            if row["r2_general_group"] > 0.9:
                r2_columns = [col for col in processed_df.columns if col.startswith("r2_group_")]
                non_null_r2_columns = [col for col in r2_columns if pd.notnull(row[col])]
                if len(non_null_r2_columns) == 1:
                    selected_groups.append(int(non_null_r2_columns[0].split("_")[-1]))
                    continue
                r2_values = {g: get_group_r2_adjusted(row, g) for g in range(num_groups)}
                max_r2 = max([r2 for r2 in r2_values.values() if r2 is not None])
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
            r2_values = {g: get_group_r2_adjusted(row, g) for g in candidates}
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

    processed_df["selected_group"] = selected_groups
    return processed_df


def process_entry_id_column(df):
    # the aim of this function is to prepare single ref multiple entry data for conflict handling without changing the complicated conflict_handling function
    # Function to check and convert string representation of lists to actual lists
    def parse_entry_id(entry):
        if isinstance(entry, str):  # If it's a string, assume it's a list in string format
            try:
                # Convert string to actual list (only works if it's a valid list string)
                return eval(entry)
            except:
                return []  # Return an empty list if eval fails
        return entry  # If it's already a list, return as-is

    df['entry_id'] = df['entry_id'].apply(parse_entry_id)

    all_unique_values = sorted(set(value for sublist in df['entry_id'] for value in sublist))

    value_to_code = {value: idx + 1 for idx, value in enumerate(all_unique_values)}

    code_to_value = {idx + 1: value for idx, value in enumerate(all_unique_values)}

    df['entry_id'] = df['entry_id'].apply(lambda x: [value_to_code[val] for val in x])

    df['ref_id'] = df['entry_id']  # this is just a manpulation to make the code work without changing the conflict_handling function

    df['entry_id'] = df['entry_id'].apply(lambda x: [code_to_value[val] for val in x])

    return df



def conflict(df, name):
    processed_data, failed_rows = process_data(df)
    save_failed_rows(failed_rows, name)

    add_regression_results(processed_data)
    expanded_rows = expand_rows(processed_data)
    df = save_processed_data(expanded_rows, name)

    df = filter_columns(df)
    df = calculate_ln_and_inv(df)
    df = rename_pseudo_group(df)
    save_filtered_data(df, name)

    random.seed(42)
    df = convert_str_to_list(df)
    df = ensure_list_values(df)
    df = apply_chow_test(df)
    df = count_false_contributions(df)
    df = determine_selected_group(df)

    output_path = f'Intermediate_Data/step9_conflicted_data_resolved_{name}.csv'
    df.to_csv(output_path, index=False)
    print(f'Processed data with selected group saved to {output_path}')
    return df


def conflict_handling(df1, df2, name1, name2):
    df1 = conflict(df1, name1)
    df2 = process_entry_id_column(df2)
    df2 = conflict(df2, name2)
    return df1, df2

if __name__ == "__main__":
    file_path1 = 'Intermediate_Data/step8_gh_multiple_ref_combinations.csv'
    file_path2 = 'Intermediate_Data/step8_single_ref_multiple_entry.csv'
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)
    # df2 = process_entry_id_column(df2)
    conflict_handling(df1, df2, 'multi', 'single')
    
    

import os
os.environ["OMP_NUM_THREADS"] = "1"
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress, ttest_ind, t



def gibbs_helmholtz_coefficients(df, target = 'gamma'):
    """
    Processes the input DataFrame, filters out combinations with fewer than threshold occurrences, 
    ranks combinations by population, and creates new DataFrames with 'ref_id' values 
    for each combination.

    Args:
        df: The input DataFrame.
        target: The name of the target column for analysis.

    Returns:
        A tuple containing:
            - gh_df: A DataFrame containing the ranked combinations and slope and intercept of Gibbs-Helmholtz equation.
            - multiple_ref_combinations: A DataFrame containing combinations with multiple 'ref_id' values to check if there are any discrepancies for gamma values.
    """
    threshold = 5
    # Ensure 'original_index' is present in the DataFrame
    if 'original_index' not in df.columns:
        raise ValueError("The input DataFrame must contain an 'original_index' column.")

    # Filter out combinations with a population less than threshold
    combination_counts = df.groupby(['IL_id', 'solute_id']).size().reset_index(name='counts')
    df = df.merge(combination_counts, on=['IL_id', 'solute_id'])
    df = df[df['counts'] >= threshold].drop(columns=['counts'])

    # Get unique combinations of IL_id and solute_id
    unique_combinations = df[['IL_id', 'solute_id']].drop_duplicates()

    # Rank the unique combinations by the population count
    gh_df = unique_combinations.copy()
    gh_df['population'] = gh_df.apply(
        lambda row: df[(df['IL_id'] == row['IL_id']) & 
                       (df['solute_id'] == row['solute_id'])].shape[0], axis=1)
    gh_df = gh_df.sort_values(by='population', ascending=False).reset_index(drop=True)

    # Assign unique rank numbers
    gh_df['unique_rank'] = range(1, len(gh_df) + 1)

    # Add 'ref_id' column with a list of 'ref_id' values for each combination
    gh_df['ref_id'] = gh_df.apply(
        lambda row: df[(df['IL_id'] == row['IL_id']) & 
                       (df['solute_id'] == row['solute_id'])]['ref_id'].tolist(), 
        axis=1)

    # Add 'original_index' column with a list of original indices for each combination
    gh_df['original_index'] = gh_df.apply(
        lambda row: df[(df['IL_id'] == row['IL_id']) & 
                       (df['solute_id'] == row['solute_id'])]['original_index'].tolist(), 
        axis=1)

    # Include all original columns in the final DataFrame
    original_columns = df.columns.tolist()
    for col in original_columns:
        if col not in gh_df.columns:
            gh_df[col] = gh_df.apply(
                lambda row: df[(df['IL_id'] == row['IL_id']) & 
                               (df['solute_id'] == row['solute_id'])][col].tolist(),
                axis=1
            )

       
    
    # Calculate intercept, slope, R-squared, t-test, p-value, rsd and normalized_mae for each combination       
    def calculate_regression_params(row):
        # Filter subset based on conditions
        subset = df[(df['IL_id'] == row['IL_id']) & 
                    (df['solute_id'] == row['solute_id'])].copy()
        subset['inv_temp'] = 1 / subset['temperature']
        subset['ln_gamma'] = np.log(subset[target])
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(subset['inv_temp'], subset['ln_gamma'])
        r_squared = r_value**2
        
        # Safeguard against invalid std_err
        if std_err == 0:
            t_stat = 0
            t_p_value = 1  # p-value for zero slope, no relationship
        else:
            t_stat = slope / std_err
            t_p_value = 2 * (1 - t.cdf(abs(t_stat), df=len(subset) - 2))
        
        # Calculate relative standard deviation (RSD) as a percentage
        mean_ln_target = subset['ln_gamma'].mean()
        std_ln_target = subset['ln_gamma'].std()
        
        # Handle cases with zero mean and non-zero standard deviation
        if std_ln_target == 0:
            rsd = 0  # No variation, set RSD to 0
        elif mean_ln_target == 0:
            # If mean is zero but standard deviation is non-zero, calculate RSD
            rsd = (std_ln_target / subset['ln_gamma'].max()) * 100  # Use max of ln_target to avoid zero division
        else:
            rsd = (std_ln_target / mean_ln_target) * 100  # Relative Standard Deviation
        
        # Calculate Mean Absolute Error (MAE)
        predicted_ln_target = intercept + slope * subset['inv_temp']
        mae = np.mean(np.abs(subset['ln_gamma'] - predicted_ln_target))
        
        # Calculate absolute value of normalized MAE
        if mean_ln_target == 0:
            normalized_mae = abs(mae / subset['ln_gamma'].max())  # Use max of ln_target to avoid zero division
        else:
            normalized_mae = abs(mae / mean_ln_target)
        
        return pd.Series({
            'intercept': intercept,
            'slope': slope,
            'r_squared': r_squared,
            't_p_value': t_p_value,
            'rsd': rsd,
            'normalized_mae': normalized_mae,
        })


    regression_params = gh_df.apply(calculate_regression_params, axis=1)
    gh_df = pd.concat([gh_df, regression_params], axis=1)

    # Identify combinations with multiple 'ref_id' values
    multiple_ref_combinations = gh_df[gh_df['ref_id'].apply(lambda x: len(set(x)) > 1)]
    single_ref_combinations = gh_df[gh_df['ref_id'].apply(lambda x: len(set(x)) == 1)]

    # Save gh_df, multiple_ref_combinations, single_ref_combinations to CSV files
    intermediate_dir = os.path.join(os.path.dirname(__file__), 'Intermediate_Data')
    os.makedirs(intermediate_dir, exist_ok=True)
    
    gh_df.to_csv(os.path.join(intermediate_dir, 'step8_gh_total.csv'), index=False)
    multiple_ref_combinations.to_csv(os.path.join(intermediate_dir, 'step8_gh_multiple_ref_combinations.csv'), index=False)
    single_ref_combinations.to_csv(os.path.join(intermediate_dir, 'step8_gh_single_ref_combinations.csv'), index=False)

    # sanity check for the sum population column for gh_df, single_ref_combinations and multiple_ref_combinations
    if gh_df['population'].sum() == single_ref_combinations['population'].sum() + multiple_ref_combinations['population'].sum():
        print("Sanity check passed: population sum of gh_df is equal to the sum of population of single_ref_combinations and multiple_ref_combinations.")
    else:
        print("Sanity check failed: population sum of gh_df is not equal to the sum of population of single_ref_combinations and multiple_ref_combinations.")
        
    return gh_df, multiple_ref_combinations, single_ref_combinations

def save_ranked_combinations(total_combinations, file_path):
    """
    Saves the ranked combinations DataFrame to a CSV file.

    Args:
        total_combinations: The DataFrame containing the ranked combinations.
        file_path: The path to the output CSV file.
    """
    intermediate_dir = os.path.join(os.path.dirname(file_path), 'Intermediate_Data')
    os.makedirs(intermediate_dir, exist_ok=True)
    total_combinations.to_csv(os.path.join(intermediate_dir, os.path.basename(file_path)), index=False)

def save_multiple_ref_combinations(multiple_ref_combinations, file_path):
    """
    Saves the DataFrame containing combinations with multiple 'ref_id' values to a CSV file.

    Args:
        multiple_ref_combinations: The DataFrame containing combinations with multiple 'ref_id' values.
        file_path: The path to the output CSV file.
    """
    intermediate_dir = os.path.join(os.path.dirname(file_path), 'Intermediate_Data')
    os.makedirs(intermediate_dir, exist_ok=True)
    multiple_ref_combinations.to_csv(os.path.join(intermediate_dir, os.path.basename(file_path)), index=False)

def save_single_ref_combinations(single_ref_combinations, file_path):
    """
    Saves the DataFrame containing combinations with single 'ref_id' values to a CSV file.

    Args:
        single_ref_combinations: The DataFrame containing combinations with single 'ref_id' values.
        file_path: The path to the output CSV file.
    """
    intermediate_dir = os.path.join(os.path.dirname(file_path), 'Intermediate_Data')
    os.makedirs(intermediate_dir, exist_ok=True)
    single_ref_combinations.to_csv(os.path.join(intermediate_dir, os.path.basename(file_path)), index=False)


if __name__ == "__main__":
    data_path = 'Intermediate_Data/step7_activity_data_elements_filtered.csv'
    df = pd.read_csv(data_path)


    # ranked_combinations_file = os.path.join(base_dir, 'step8_gh_total.csv')  # gh stands for Gibbs-Helmholtz
    # multiple_ref_combinations_file = os.path.join(base_dir, 'step8_gh_multiple_ref_combinations.csv')
    # single_ref_combinations_file = os.path.join(base_dir, 'step8_gh_single_ref_combinations.csv')

    # Process data and save ranked combinations
    total_combinations, multiple_ref_combinations, single_ref_combinations = gibbs_helmholtz_coefficients(df)
    # save_ranked_combinations(total_combinations, ranked_combinations_file)
    # save_multiple_ref_combinations(multiple_ref_combinations, multiple_ref_combinations_file)
    # save_single_ref_combinations(single_ref_combinations, single_ref_combinations_file)



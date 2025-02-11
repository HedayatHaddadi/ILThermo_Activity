import pandas as pd

def docode_data(df):
    """Processes a DataFrame row by row, handling empty 'V4' values and 
       assigning values to new columns based on conditions in V1, V2, and V3.

    Args:
        df: The Pandas DataFrame to process.

    Returns:
        A copy of the processed Pandas DataFrame.
    """
    df_copy = df.copy()
    df_copy['original_index'] = df_copy.index  # Store original index
    # remove rows with 'solvent' column water, methanol, ethanol, propan-1-ol
    df_copy = df_copy[~df_copy['solvent'].str.lower().isin(['water', 'methanol', 'ethanol', 'propan-1-ol'])] # check for other solvents as needed or remove this line if not needed
    

    # Initialize new columns
    df_copy['temperature'] = None
    df_copy['pressure'] = None
    df_copy['mole_fraction'] = None

    try:
        for index, row in df_copy.iterrows():
            if pd.isna(row['V4']):
                df_copy.loc[index, 'temp_gamma'] = row['V3']
                df_copy.loc[index, 'V4'] = df_copy.loc[index, 'temp_gamma']
                df_copy.loc[index, 'V3'] = None

        # Create gamma column from V4
        df_copy['gamma'] = df_copy['V4']

        df_copy = df_copy.drop(columns=['temp_gamma'], errors='ignore')

        # Assign values based on conditions in V1, V2, V3 (outside the row loop)
        for col in ['V1', 'V2', 'V3']:
            df_copy.loc[df_copy[col].between(98, 102, inclusive='both'), 'pressure'] = df_copy[col]  #To maintain constant pressure for all samples (additionally, a very small portion of samples are removed).
            df_copy.loc[df_copy[col] > 250, 'temperature'] = df_copy[col]
            df_copy.loc[df_copy[col] < 5, 'mole_fraction'] = df_copy[col]

        # Sanity check
        df_copy['sum_original'] = df_copy[['V1', 'V2', 'V3', 'V4']].sum(axis=1, skipna=True)
        df_copy['sum_new'] = df_copy[['pressure', 'temperature', 'mole_fraction', 'gamma']].sum(axis=1, skipna=True)
        df_copy['sanity_check'] = (df_copy['sum_original'] - df_copy['sum_new']).abs() < 1e-6
        
        # Report rows that fail the sanity check
        failed_sanity_check = df_copy[~df_copy['sanity_check']]
        if not failed_sanity_check.empty:
            failed_sanity_check.to_csv('Intermediate_Data/step2_sanity_check_failed_rows_for_column_adjusment.csv', index=False)
            print("Warning: Some rows failed the sanity check due to significant discrepancies in experimental parameters, such as pressure, compared to the rest of the samples. Consequently they have been removed. Check 'step2_sanity_check_failed_rows.csv'.")
            print(f"Number of failed rows: {failed_sanity_check.shape[0]}")
        
        df_copy = df_copy.sort_values(by='original_index').drop(columns=['original_index', 'sum_original', 'sum_new'])
        df_copy = df_copy[df_copy['sanity_check']]
        df_copy = df_copy.drop(columns=['sanity_check'])
        df_copy = df_copy[df_copy['mole_fraction'] < 1e-5]  # Retain rows with a mole fraction less than 1e-5 to be considered as infinite dilution. Remove this line if it is not needed based on your goal.
        print(f"Processed DataFrame shape: {df_copy.shape}")
        # Save to CSV
        df_copy.to_csv('Intermediate_Data/step2_columns_adjusted.csv', index=False)
        return df_copy


    except KeyError:
        print("Error: Columns 'V1', 'V2', 'V3', or 'V4' not found in DataFrame.")
        return df.copy()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")        
        return df_copy.copy()

if __name__ == "__main__":
    
    raw_data = pd.read_csv('Intermediate_Data/step1_raw_activity_data.csv')
    adjusted_data = docode_data(raw_data)


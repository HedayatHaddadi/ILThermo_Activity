import os

import pandas as pd



base_dir = os.getcwd()
file_path = os.path.join(base_dir, 'updated_activity_data_filled_place_smiles.csv')
output_file = os.path.join(base_dir, 'cleaned_activity_data.csv')


ref_rem = "{'full': 'Domanska, U.; Marciniak, A. (2010) J. Phys. Chem. B 112(35), 11100-11105.', 'title': 'Activity Coefficients at Infinite Dilution Measurements for Organic Solutes and Water in the Ionic Liquid 1-Butyl-3-methylimidazolium Trifluoromethanesulfonate'}"

# remove all rows with the ref_rem value and save the cleaned data
df = pd.read_csv(file_path, dtype={'ref': str}, low_memory=False)
df = df[df.ref != ref_rem]
df.to_csv(output_file, index=False)
print(f"Data cleaned and saved to {output_file}")
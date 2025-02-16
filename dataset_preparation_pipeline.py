# dataset_preparation_pipeline.py

from step1_retrieving_data import get_and_combine_data
from step2_decode_data import docode_data
from step3_get_smiles import get_smiles
from step4_missing_smiles import missing_smiles
from step5_place_smiles import place_smiles
from step6_duplicate_refs import duplicate_refs
from step7_elemental_filter import elemental_filtering
from step8_gibbs_helmholtz import gibbs_helmholtz_coefficients
from step9_conflict_handling import conflict_handling
from step10_final_cleaning import finalizing_data
import pandas as pd
import warnings

warnings.filterwarnings("ignore")



# Define the search parameters dictionary
search_params = {
    "prop_key": "BPpY",  # Modify with correct property key if needed. Use ilt.ShowPropertyList() to get the list of property keys.
    "n_compounds": 2
    # Additional parameters can be added here. Refer to ilthermopy.search.Search for more options.
}

def dataset_preparation_pipeline():

    # # raw_data = get_and_combine_data(search_params, max_workers=4)   
    # raw_data = pd.read_csv('Intermediate_Data/step1_raw_activity_data.csv')

    # adjusted_data = docode_data(raw_data)  

    # smiles_data = get_smiles(adjusted_data)     
    smiles_data = pd.read_csv('Intermediate_Data/step3_smiles_added.csv')
    
    filled_smiles_data = missing_smiles(smiles_data)    

    placed_smiles_data = place_smiles(filled_smiles_data)   

    deduped_data = duplicate_refs(placed_smiles_data) 

    filtered_data = elemental_filtering(deduped_data)   

    _, multiple_ref_combinations, single_ref_multiple_entry, _ = gibbs_helmholtz_coefficients(filtered_data) 

    conflict_handling(multiple_ref_combinations, single_ref_multiple_entry, 'multi', 'single')    

    final_data = finalizing_data()   

    return final_data
    


if __name__ == "__main__":
    dataset_preparation_pipeline()

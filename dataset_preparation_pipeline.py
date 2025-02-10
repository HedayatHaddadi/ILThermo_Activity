# dataset_preparation_pipeline.py

from step1_retrieving_data import get_and_combine_data
from step2_decode_exp_data import process_dataframe
from step3_get_smiles import get_smiles
from step4_missing_smiles import missing_smiles
from step5_place_smiles import place_smiles
from step6_duplicate_refs import duplicate_refs
from step7_elemental_filter import elemental_filtering
from step8_gibbs_helmholtz import gibbs_helmholtz_coefficients
from step9_plot_ranks import visualize_all_ranks
from step10_conflict_handling import conflict_handling
from step11_final_cleaning import finalizing_data



# Define the search parameters dictionary
search_params = {
    "prop_key": "BPpY",  # Modify with correct property key if needed. Use ilt.ShowPropertyList() to get the list of property keys
    "n_compounds": 2
    # Additional parameters can be added here. Refer to ilthermopy.search.Search for more options.
}

def dataset_preparation_pipeline():

    raw_data = get_and_combine_data(search_params, max_workers=4)   # step1_raw_activity_data.csv

    adjusted_data = process_dataframe(raw_data)   # step2_columns_adjusted.csv

    smiles_data = get_smiles(adjusted_data)     # step3_smiles_added.csv
    
    filled_smiles_data = missing_smiles(smiles_data)     # step4_missing_smiles_added.csv

    placed_smiles_data = place_smiles(filled_smiles_data)    # step5_place_smiles_for_IL_and_solute.csv

    deduped_data = duplicate_refs(placed_smiles_data)   # step6_activity_data_removed_duplicate_refs.csv

    filtered_data = elemental_filtering(deduped_data)    # step7_activity_data_elements_filtered.csv

    _, gh_multiple_refs, gh_single_refs = gibbs_helmholtz_coefficients(filtered_data)   # gh_multiple_ref_combinations.csv, gh_single_ref_combinations.csv, gh stands for Gibbs-Helmholtz

    visualize_all_ranks(gh_multiple_refs)

    resolved_conflicts_data = conflict_handling(gh_multiple_refs)    # step10_conflicted_data_resolved.csv

    final_data = finalizing_data(resolved_conflicts_data, gh_single_refs, filtered_data)   # step11_final_refined_activity_dataset.csv

    return final_data
    


if __name__ == "__main__":
    dataset_preparation_pipeline()

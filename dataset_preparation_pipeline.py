# dataset_preparation_pipeline.py

import pandas as pd
from step1_retrieving_data import get_and_combine_data, search_params
from step2_decode_exp_data import process_dataframe
from step3_get_smiles import get_smiles
from step4_missing_smiles import missing_smiles
from step5_place_smiles import place_smiles
from step6_duplicate_refs import duplicate_refs
from step7_elemental_filter import process_dataset
from step8_gibbs_helmholtz import gibbs_helmholtz_coefficients
from step9_plot_ranks import visualize_all_ranks
from step10_conflict_handling import conflict_handling
from step11_final_cleaning import finalizing_data



def dataset_preparation_pipeline():

    df_1 = get_and_combine_data(search_params, max_workers=4)

    df_2 = process_dataframe(df_1)

    df_3 = get_smiles(df_2)
    
    df_4 = missing_smiles(df_3)

    df_5 = place_smiles(df_4)

    df_6 = duplicate_refs(df_5)

    df_7 = process_dataset(df_6)

    _, df_8_1, df_8_2 = gibbs_helmholtz_coefficients(df_7)

    visualize_all_ranks(df_8_1)

    df_10 = conflict_handling(df_8_1)

    df_11 = finalizing_data(df_10, df_8_2, df_7)

    return df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8_1, df_8_2, df_10, df_11
    


if __name__ == "__main__":
    dataset_preparation_pipeline()

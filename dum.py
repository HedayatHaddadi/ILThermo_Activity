def separate_entries(single_ref_combinations):
    single_ref_combinations['unique_entry_id_count'] = single_ref_combinations['entry_id'].apply(lambda x: len(set(eval(x))))
    single_ref_multiple_entry = single_ref_combinations.loc[single_ref_combinations['unique_entry_id_count'] > 1].copy()
    single_ref_multiple_entry.drop(columns=['unique_entry_id_count'], inplace=True)
    single_ref_single_entry = single_ref_combinations.loc[single_ref_combinations['unique_entry_id_count'] == 1].copy()
    single_ref_single_entry.drop(columns=['unique_entry_id_count'], inplace=True)
    return single_ref_single_entry, single_ref_multiple_entry

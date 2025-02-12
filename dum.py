def process_entry_id_column(df):
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

    df['ref_id'] = df['entry_id']

    df['entry_id'] = df['entry_id'].apply(lambda x: [code_to_value[val] for val in x])

    return df



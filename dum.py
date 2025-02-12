


import pandas as pd

threshold = 5
step8_df = pd.read_csv("Intermediate_Data/step8_gh_single_ref_combinations.csv")
print(step8_df.shape)
print(step8_df[step8_df['population'] >= threshold].shape[0])
print(step8_df[step8_df['population'] >= threshold].shape[0] / step8_df.shape[0] * 100)


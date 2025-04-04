# ILThermo Data Processing and Conflict Detection

This repository contains Python scripts designed for retrieving, processing, and refining thermophysical data from the ILThermo 2.0 database. 
The primary goal is to enhance data reliability for machine learning applications by ensuring data integrity and resolving conflicts using statistical methods.

## Dataset Processing and Preparation
- Retrieves ILThermo 2.0 data using the ILThermoPy package (as of June 4, 2024).
- Cleans and structures data, handling missing values and removing redundant entries.
- Enriches data with SMILES representations for accurate component identification.
- Eliminates duplicate references and filters entries to retain only commonly used elements.


## Conflict Detection Using the Gibbs-Helmholtz Approach
- Ensures data consistency by analyzing IL-solute systems across different sources and conditions.
- Applies the Gibbs-Helmholtz equation to identify discrepancies in thermodynamic trends.
- Categorizes IL-solute combinations into single-source, multiple-source, and different-condition groups.
- Resolves or excludes conflicting data.

By running the scripts successively from `step1` to the final step, the entire pipeline—from retrieving raw data from the ILThermo database to preparing the final cleaned dataset—will be executed automatically. 
The `dataset` folder contains both the raw retrieved data and the final refined dataset in CSV format.
Additional scripts are included for reproducing key results from the article, such as performing Gibbs-Helmholtz regression, plotting data, and conducting t-tests.



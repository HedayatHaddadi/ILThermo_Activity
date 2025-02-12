# Data Processing and Grouping Methodology

## Overview

This document outlines the methodology used to process, filter, and analyze data, including criteria for regression analysis, handling of groupings, and filtering based on key parameters. It also specifies the required hyperparameters for the analysis.

## Criteria and Hyperparameters

### 1. **Grouping Criteria**

Data is grouped based on the `ref_id` values:

- **General Group**: All data points are included in the general group.
- **Group Assignment**: If a `ref_id` has 3 or more samples, it is assigned to a specific group (e.g., `group_1`, `group_2`, etc.).
- **Pseudo Group**: Any `ref_id` with fewer than 3 samples is assigned to the `seudo_group`.

### 2. **Regression Analysis Criteria**

For each group:

- **Regression Model**: Linear regression of \( \ln(\gamma) \) vs. \( \frac{1}{T} \), where:
  - \( T \) is the temperature.
  - \( \gamma \) is the activity coefficient.
- **Key Metrics**:
  - **Slope**: The slope of the regression line.
  - **Intercept**: The intercept of the regression line.
  - **R² (Coefficient of Determination)**: A measure of how well the regression model fits the data. It should be calculated for each group.

### 3. **Hyperparameters**

- **Group Size**: 
  - A `ref_id` with fewer than 3 samples is grouped under `seudo_group`.
  - `ref_id` values with at least 3 samples are assigned to specific groups (e.g., `group_1`, `group_2`, etc.).
  
- **Threshold for Retaining Rows**: 
  - If a row belongs to a `seudo_group` and contains only samples from `seudo_group`, no t-test is applied. In such cases, the row is retained if the **R²** value is greater than 0.9. Otherwise, the row is rejected.
  - If a row contains multiple groups (e.g., a mix of groups such as `group_0`, ...), statistical tests (Chow tests) is applied to evaluate the difference between regression fit (the slopes and intercepts) of the groups.
  - Rows with no significant differences (p-value < 0.05 from the Chow tests) are retained if they meet the specified **R²** and other filtering criteria.

  
### 4. **Statistical Tests**

- **Chow Test**: A statistical test to evaluate if there are significant differences between two groups.
  - Groups with fewer than 3 samples are excluded from the Chow test.
  - The **F-statistic** and **p-value** are computed for each pair of groups.
  - If the p-value is less than 0.05, the difference between the groups is considered significant.

### 5. **Data Filtering and Group Refinement**

- **Invalid Rows**: Any rows that fail to meet the grouping criteria or regression conditions are flagged and saved for review.
- **Final Output**: A final dataset is created that includes only the rows passing all criteria, with added regression results and statistical test outcomes.

## Detailed Data Processing Steps

### 1. **Load Dataset**

Data is loaded from a specified CSV file.

### 2. **Process Row**

Each row in the dataset is processed to group the data by `ref_id`, and the regression analysis is performed.

### 3. **Regression Analysis**

For each group, the regression of \( \ln(\gamma) \) vs. \( \frac{1}{T} \) is computed.

### 4. **Statistical Testing**

The Chow test is applied between groups with more than 2 samples to check for statistical differences.

### 5. **Save Processed Data**

After filtering and processing, the final dataset is saved to a CSV file.

## Conclusion

This methodology ensures that data is grouped, analyzed, and filtered based on rigorous criteria and statistical tests, ensuring the integrity and quality of the dataset for further analysis.

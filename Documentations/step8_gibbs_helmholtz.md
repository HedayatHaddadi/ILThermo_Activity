### Step 8: **gibbs_helmholtz_coefficients.py**

This script processes the dataset to extract combinations of ionic liquids and solutes, ranks them by their population, and calculates various regression parameters, including intercept, slope, R-squared, t-test p-value, relative standard deviation (RSD), and normalized mean absolute error (MAE). It then saves the results into separate CSV files and performs a sanity check on the population sums.

**Key Functions:**
1. **`gibbs_helmholtz_coefficients`**: 
    - Filters the data for combinations with a population greater than or equal to 3 (`population >= 3`).
    - Ranks combinations by population in descending order.
    - Assigns unique ranks to combinations based on their population.
    - Adds `ref_id` (list of unique references for each combination) and `original_index` (list of indices for each combination).
    - Performs regression analysis:
        - Linear regression is performed with the equation \( \ln \gamma = \text{intercept} + \text{slope} \cdot \left( \frac{1}{T} \right) \).
        - The regression metrics include:
            - **Intercept**: The y-intercept of the linear fit.
            - **Slope**: The slope of the linear fit.
            - **R-squared**: A measure of the goodness of fit.
            - **t-test p-value**: The p-value from a t-test on the slope to assess its significance.
            - **RSD (Relative Standard Deviation)**: A measure of the variability in the data, calculated as \( \frac{\text{std dev}}{\text{mean}} \times 100 \).
            - **Normalized MAE (Mean Absolute Error)**: The normalized error between the predicted and actual values of \( \ln \gamma \).
        - If the standard error of the slope is zero, the t-test result is adjusted to indicate no significant relationship.
    - Identifies combinations with multiple `ref_id` values and separates them from those with a single `ref_id`.

2. **`save_ranked_combinations`**: 
    - Saves the DataFrame containing the ranked combinations to a CSV file.

3. **`save_multiple_ref_combinations`**: 
    - Saves the DataFrame containing combinations with multiple `ref_id` values to a CSV file.

4. **`save_single_ref_combinations`**: 
    - Saves the DataFrame containing combinations with single `ref_id` values to a CSV file.

**Hyper-parameters, Thresholds, and Criteria:**

1. **Population Threshold for Filtering Combinations**:
   - **Criterion**: Only combinations with a population (number of occurrences) of at least 3 are retained.
   - **Threshold**: `population >= 3`

2. **Linear Regression Parameters**:
   - **Target Variable**: `gamma` (used to calculate \( \ln \gamma \)).
   - **Independent Variable**: Inverse temperature (\( \frac{1}{T} \)).
   - **Regression Equation**: \( \ln \gamma = \text{intercept} + \text{slope} \cdot \left( \frac{1}{T} \right) \).

3. **Relative Standard Deviation (RSD)**:
   - **Criterion**: RSD is calculated as \( \frac{\text{std dev of ln_gamma}}{\text{mean of ln_gamma}} \times 100 \).
   - **Alternative Calculation for Zero Mean**: If the mean \( \ln \gamma \) is zero, RSD is calculated based on the maximum value of \( \ln \gamma \) to avoid division by zero.

4. **Normalized Mean Absolute Error (MAE)**:
   - **Criterion**: The normalized MAE is calculated by dividing the MAE by the mean of \( \ln \gamma \). If the mean is zero, the maximum value is used instead.
   - **Threshold**: No specific threshold applied here, but the value provides an assessment of prediction accuracy.

5. **T-test for Slope**:
   - **Criterion**: A t-test is performed to assess the statistical significance of the regression slope. A p-value of less than 0.05 generally indicates a significant relationship.
   - **Formula**: \( t_{\text{stat}} = \frac{\text{slope}}{\text{std error}} \) with the p-value calculated from the t-distribution.

**Output:**
- The script generates and saves the following CSV files in the `Intermediate_Data` directory:
  - **`step8_gh_total.csv`**: Contains the ranked combinations, regression parameters, and additional details.
  - **`step8_gh_multiple_ref_combinations.csv`**: Contains combinations with multiple `ref_id` values.
  - **`step8_gh_single_ref_combinations.csv`**: Contains combinations with single `ref_id` values.
- **Sanity Check**: The sum of the populations in the `gh_df`, `single_ref_combinations`, and `multiple_ref_combinations` DataFrames is verified to ensure the data integrity:
  - The total population from `gh_df` should match the sum of the populations in `single_ref_combinations` and `multiple_ref_combinations`.

**Usage:**
- This script is designed to process and analyze data involving combinations of ionic liquids and solutes, focusing on statistical analysis of their Gibbs-Helmholtz equation parameters.
- It is particularly useful for evaluating the reliability of data, detecting discrepancies in the dataset, and assessing the quality of predictions based on regression models.

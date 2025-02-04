import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from tqdm import tqdm  

def visualize_all_ranks(file_path, target, output_dir, batch_size=100, specific_ranks=None):
    """
    Visualizes the relationship between 1/T/K and the logarithm of the target column
    for all ranks or specific ranks in the dataset, optimized for large-scale processing.

    Args:
        file_path: Path to the prepared gh_dataset.csv file.
        target: The name of the target column.
        output_dir: Directory to save the plots.
        batch_size: Number of ranks to process in each batch.
        specific_ranks: List of specific ranks to plot. If None, all ranks are plotted.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    os.makedirs(output_dir, exist_ok=True)

    # Load the dataset
    ranked_combinations = pd.read_csv(file_path)

    # Filter for specific ranks if provided
    if specific_ranks is not None:
        ranked_combinations = ranked_combinations[ranked_combinations['unique_rank'].isin(specific_ranks)]
        if ranked_combinations.empty:
            raise ValueError("No matching ranks found in the dataset for the provided specific_ranks.")

    # Get the total number of ranks
    total_ranks = len(ranked_combinations)

    print(f"Processing {total_ranks} ranks...")

    # Process ranks in batches
    for start_idx in tqdm(range(0, total_ranks, batch_size), desc="Generating Plots"):
        end_idx = min(start_idx + batch_size, total_ranks)
        batch = ranked_combinations.iloc[start_idx:end_idx]

        for _, row in batch.iterrows():
            try:
                # Extract data for the current rank
                il_id = row['IL_id']
                sol_id = row['solute_id']
                subset_data = pd.DataFrame({
                    'T/K': eval(row['T/K']),
                    target: eval(row[target])
                })

                # Calculate 1/T/K and ln(target)
                subset_data['1_T_K'] = 1 / subset_data['T/K']
                subset_data['ln_target'] = np.log(subset_data[target])

                # Perform linear regression
                slope, intercept, r_value, _, _ = linregress(subset_data['1_T_K'], subset_data['ln_target'])
                r_squared = r_value**2

                # Plot the data
                plt.figure(figsize=(10, 6))
                plt.scatter(subset_data['1_T_K'], subset_data['ln_target'], label='Data Points')
                plt.plot(subset_data['1_T_K'], intercept + slope * subset_data['1_T_K'], color='red', 
                         label=f'y = {intercept:.4f} + {slope:.4f}x')
                plt.title(f"Rank {row['unique_rank']}: {il_id} & {sol_id}\nR² = {r_squared:.4f}")
                plt.xlabel('1/T/K')
                plt.ylabel(f'ln({target})')
                plt.legend()

                # Save the plot
                plot_path = os.path.join(output_dir, f"rank_{row['unique_rank']}.png")
                plt.savefig(plot_path)
                plt.close()

            except Exception as e:
                print(f"Error processing rank {row['unique_rank']}: {e}")

    print(f"All plots saved to {output_dir}")

if __name__ == "__main__":
    
    base_dir = os.getcwd()
    file_path = os.path.join(base_dir, 'Outputs', 'gh_dataset.csv')
    output_dir = os.path.join(base_dir, 'Outputs', 'Plots_Ref_43')  # set the output directory for the plots such as 'Outputs/Plots_Ref_43' based on the reference or your task
    target = 'IDAC_exp'

    # Plot specific ranks
    specific_ranks = [1, 2, 3, 5, 7, 17, 19, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 56, 448, 484, 538, 545, 563, 580, 748, 799, 988, 3512] # Replace with desired ranks or set to None for all ranks, all is time consuming

    visualize_all_ranks(file_path, target, output_dir, batch_size=100, specific_ranks=specific_ranks)

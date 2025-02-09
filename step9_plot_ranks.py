import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from tqdm import tqdm  

def visualize_all_ranks(ranked_combinations, target = 'gamma', batch_size=100, specific_ranks=None):
    """
    Visualizes the relationship between 1/temperature and the logarithm of the target column
    for all ranks or specific ranks in the dataset, optimized for large-scale processing.

    Args:
        file_path: Path to the prepared gh_dataset.csv file.
        target: The name of the target column.
        output_dir: Directory to save the plots.
        batch_size: Number of ranks to process in each batch.
        specific_ranks: List of specific ranks to plot. If None, all ranks are plotted.
    """
    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, 'plots')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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
                    'temperature': eval(row['temperature']),
                    target: eval(row[target])
                })

                # Calculate 1/temperature and ln(target)
                subset_data['temperature'] = 1 / subset_data['temperature']
                subset_data['ln_gamma'] = np.log(subset_data[target])

                # Perform linear regression
                slope, intercept, r_value, _, _ = linregress(subset_data['temperature'], subset_data['ln_gamma'])
                r_squared = r_value**2

                # Plot the data
                plt.figure(figsize=(10, 6))
                plt.scatter(subset_data['temperature'], subset_data['ln_gamma'], label='Data Points')
                plt.plot(subset_data['temperature'], intercept + slope * subset_data['temperature'], color='red', 
                         label=f'y = {intercept:.4f} + {slope:.4f}x')
                plt.title(f"Rank {row['unique_rank']}: {il_id} & {sol_id}\nR² = {r_squared:.4f}")
                plt.xlabel('1/temperature')
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
    file_path = os.path.join(base_dir, 'step8_gh_filtered_activity_data_multiple.csv')
    ranked_combinations = pd.read_csv(file_path)

    visualize_all_ranks(ranked_combinations)

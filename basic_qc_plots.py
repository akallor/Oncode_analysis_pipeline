import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(filepath):
    """Loads the TSV data into a pandas DataFrame."""
    try:
        df = pd.read_csv(filepath, sep=',', engine='python')
        print("Successfully loaded the data.")
        # Clean up filenames for better plotting
        df['short_filename'] = df['filename'].apply(lambda x: x.split('Rep#')[1].split('_Slot')[0] if 'Rep#' in x else x)
        return df
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        print("Please ensure the report is in the same directory as this script.")
        return None

def plot_file_sizes(df, output_dir):
    """Creates and saves a bar plot for file sizes."""
    plt.figure(figsize=(10, 6))
    sns.barplot(x='short_filename', y='file_size_mb', data=df)
    plt.title('File Size Comparison')
    plt.xlabel('Sample')
    plt.ylabel('File Size (MB)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    save_path = os.path.join(output_dir, 'file_sizes.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved file size plot to {save_path}")

def plot_spectra_counts(df, output_dir):
    """Creates and saves a stacked bar plot for spectra counts."""
    df_spectra = df[['short_filename', 'ms1_spectra', 'ms2_spectra']]
    df_spectra.set_index('short_filename').plot(kind='bar', stacked=True, figsize=(10, 7))
    plt.title('MS1 vs MS2 Spectra Counts')
    plt.xlabel('Sample')
    plt.ylabel('Number of Spectra')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    save_path = os.path.join(output_dir, 'spectra_counts.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved spectra counts plot to {save_path}")

def plot_rt_ranges(df, output_dir):
    """
    Creates a plot to visualize the retention time (RT) range for each sample.
    This plot shows the min to max RT for each file, which is more informative
    than a histogram for this type of summary data.
    """
    plt.figure(figsize=(12, 8))
    # Create a 'range' bar starting at min_rt
    plt.barh(y=df['short_filename'], width=df['max_rt'] - df['min_rt'], left=df['min_rt'])
    plt.title('Retention Time (RT) Range per Sample')
    plt.xlabel('Retention Time (minutes)')
    plt.ylabel('Sample')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    save_path = os.path.join(output_dir, 'rt_ranges.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved RT range plot to {save_path}")

def plot_mz_ranges(df, output_dir):
    """
    Creates a plot to visualize the m/z range for each sample.
    This shows the effective m/z range covered in each run.
    """
    plt.figure(figsize=(12, 8))
    # Plotting on a log scale can be helpful if max values are very large
    plt.barh(y=df['short_filename'], width=df['max_mz'] - df['min_mz'], left=df['min_mz'])
    plt.title('Mass-to-Charge (m/z) Range per Sample')
    plt.xlabel('m/z')
    plt.ylabel('Sample')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    save_path = os.path.join(output_dir, 'mz_ranges.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved m/z range plot to {save_path}")


def main():
    """Main function to generate all visualizations."""
    report_file = '/content/drive/MyDrive/Utrecht_Oncode_pipeline/mzML_integrity_report_20250622_183102.csv'
    output_dir = '/content/drive/MyDrive/Utrecht_Oncode_pipeline/visualizations'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = load_data(report_file)
    print(df.columns)
    
    if df is not None:
        plot_file_sizes(df, output_dir)
        plot_spectra_counts(df, output_dir)
        plot_rt_ranges(df, output_dir)
        plot_mz_ranges(df, output_dir)
        print("\\nAll visualization have been generated and saved in the 'visualizations' directory.")

if __name__ == '__main__':
    main() 

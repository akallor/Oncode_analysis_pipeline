#!/usr/bin/env python3
"""
Script to visualize peptide intensity and spectral count distributions
from FragPipe peptide.tsv output, separating canonical and fusion peptides.
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
from matplotlib.patches import Patch
warnings.filterwarnings('ignore')

def load_and_process_peptide_data(exp_file):
    """
    Load peptide.tsv file and separate canonical vs fusion peptides.
    
    Args:
        exp_file (str): Path to peptide.tsv file
        
    Returns:
        tuple: (canonical_df, fusion_df)
    """
    print(f"Loading peptide data from: {exp_file}")
    
    # Load the peptide data
    df = pd.read_csv(exp_file, sep='\t')
    
    # Check if required columns exist
    required_cols = ['Peptide', 'Spectral Count', 'Intensity', 'Protein']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Separate canonical and fusion peptides
    # Fusion peptides contain "fus" in the Protein column
    fusion_mask = df['Protein'].str.contains('fus', case=False, na=False)
    
    canonical_df = df[~fusion_mask].copy()
    fusion_df = df[fusion_mask].copy()
    
    print(f"Total peptides: {len(df)}")
    print(f"Canonical peptides: {len(canonical_df)}")
    print(f"Fusion peptides: {len(fusion_df)}")
    
    # Convert intensity to numeric, handling any non-numeric values
    for df_subset in [canonical_df, fusion_df]:
        df_subset['Intensity'] = pd.to_numeric(df_subset['Intensity'], errors='coerce')
        df_subset['Spectral Count'] = pd.to_numeric(df_subset['Spectral Count'], errors='coerce')
    
    return canonical_df, fusion_df

def create_filled_kde(ax, data, color, label, alpha=0.3, linewidth=2, bw_adjust=1):
    """
    Plot a filled KDE curve on the given axis.
    """
    if len(data) > 1 and np.std(data) > 0:
        kde = sns.kdeplot(data, color=color, label=label, linewidth=linewidth, ax=ax, bw_adjust=bw_adjust)
        lines = kde.get_lines()
        if len(lines) > 0:
            x, y = lines[-1].get_data()
            ax.fill_between(x, y, color=color, alpha=alpha)

def create_distribution_plots(canonical_df, fusion_df, output_prefix, psm_file=None):
    """
    Create intensity, spectral count, and retention time distribution plots, showing only KDE (density) curves.
    Args:
        canonical_df (pd.DataFrame): Canonical peptide data
        fusion_df (pd.DataFrame): Fusion peptide data
        output_prefix (str): Output file prefix
        psm_file (str): Path to psm.tsv file from FragPipe output (for retention time KDE plot)
    """
    plt.style.use('default')
    sns.set_palette("husl")
    canonical_color = '#2E86AB'
    fusion_color = '#A23B72'

    # --- Intensity KDE Plot ---
    fig, ax = plt.subplots(figsize=(8, 6))
    canonical_intensities = canonical_df['Intensity'].dropna()
    fusion_intensities = fusion_df['Intensity'].dropna()
    create_filled_kde(ax, canonical_intensities, canonical_color, 'Canonical KDE')
    create_filled_kde(ax, fusion_intensities, fusion_color, 'Fusion KDE')
    ax.set_title('Peptide Intensity Density', fontsize=14, fontweight='bold')
    ax.set_xlabel('Intensity', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    if len(canonical_intensities) > 0 and len(fusion_intensities) > 0:
        all_intensities = pd.concat([canonical_intensities, fusion_intensities])
        if all_intensities.max() > 0 and all_intensities.max() / (all_intensities[all_intensities > 0].min() or 1) > 100:
            ax.set_xscale('log')
            ax.set_xlabel('Intensity (log scale)', fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_intensity_density.png", dpi=400, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_intensity_density.pdf", bbox_inches='tight')
    plt.close()

    # --- Spectral Count KDE Plot ---
    fig, ax = plt.subplots(figsize=(8, 6))
    canonical_counts = canonical_df['Spectral Count'].dropna()
    fusion_counts = fusion_df['Spectral Count'].dropna()
    create_filled_kde(ax, canonical_counts, canonical_color, 'Canonical KDE')
    create_filled_kde(ax, fusion_counts, fusion_color, 'Fusion KDE')
    ax.set_title('Peptide Spectral Count Density', fontsize=14, fontweight='bold')
    ax.set_xlabel('Spectral Count', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_spectral_count_density.png", dpi=400, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_spectral_count_density.pdf", bbox_inches='tight')
    plt.close()

    # --- Retention Time KDE Plot (from psm.tsv) ---
    if psm_file is not None:
        try:
            psm_df = pd.read_csv(psm_file, sep='\t')
            if 'Retention' not in psm_df.columns or 'Peptide' not in psm_df.columns or 'Protein' not in psm_df.columns:
                raise ValueError('psm.tsv must contain Retention, Peptide, and Protein columns.')
            # Mark fusion vs canonical by Protein column containing "fus"
            fusion_mask = psm_df['Protein'].astype(str).str.contains('fus', case=False, na=False)
            canonical_ret = psm_df.loc[~fusion_mask, 'Retention'].dropna()
            fusion_ret = psm_df.loc[fusion_mask, 'Retention'].dropna()
            fig, ax = plt.subplots(figsize=(8, 6))
            create_filled_kde(ax, canonical_ret, canonical_color, 'Canonical KDE', bw_adjust=1.2)
            create_filled_kde(ax, fusion_ret, fusion_color, 'Fusion KDE', bw_adjust=1.2)
            ax.set_title('Peptide Retention Time Density', fontsize=14, fontweight='bold')
            ax.set_xlabel('Retention Time', fontsize=12)
            ax.set_ylabel('Density', fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_prefix}_retention_density.png", dpi=400, bbox_inches='tight')
            plt.savefig(f"{output_prefix}_retention_density.pdf", bbox_inches='tight')
            plt.close()
            print(f"  {output_prefix}_retention_density.png/pdf")
        except Exception as e:
            print(f"Could not plot retention time KDE: {e}")

    print(f"Plots saved as:")
    print(f"  {output_prefix}_intensity_density.png/pdf")
    print(f"  {output_prefix}_spectral_count_density.png/pdf")

def create_summary_statistics(canonical_df, fusion_df, output_prefix):
    """
    Create summary statistics and save to file.
    
    Args:
        canonical_df (pd.DataFrame): Canonical peptide data
        fusion_df (pd.DataFrame): Fusion peptide data
        output_prefix (str): Output file prefix
    """
    stats = []
    
    # Canonical peptide statistics
    if len(canonical_df) > 0:
        canonical_intensity_stats = canonical_df['Intensity'].describe()
        canonical_count_stats = canonical_df['Spectral Count'].describe()
        
        stats.append({
            'Category': 'Canonical',
            'Count': len(canonical_df),
            'Intensity_Mean': canonical_intensity_stats['mean'],
            'Intensity_Median': canonical_intensity_stats['50%'],
            'Intensity_Std': canonical_intensity_stats['std'],
            'SpectralCount_Mean': canonical_count_stats['mean'],
            'SpectralCount_Median': canonical_count_stats['50%'],
            'SpectralCount_Std': canonical_count_stats['std']
        })
    
    # Fusion peptide statistics
    if len(fusion_df) > 0:
        fusion_intensity_stats = fusion_df['Intensity'].describe()
        fusion_count_stats = fusion_df['Spectral Count'].describe()
        
        stats.append({
            'Category': 'Fusion',
            'Count': len(fusion_df),
            'Intensity_Mean': fusion_intensity_stats['mean'],
            'Intensity_Median': fusion_intensity_stats['50%'],
            'Intensity_Std': fusion_intensity_stats['std'],
            'SpectralCount_Mean': fusion_count_stats['mean'],
            'SpectralCount_Median': fusion_count_stats['50%'],
            'SpectralCount_Std': fusion_count_stats['std']
        })
    
    # Create summary DataFrame and save
    summary_df = pd.DataFrame(stats)
    summary_df.to_csv(f"{output_prefix}_summary_stats.csv", index=False)
    
    print(f"Summary statistics saved to: {output_prefix}_summary_stats.csv")
    print("\nSummary Statistics:")
    print(summary_df.to_string(index=False))

def main():
    parser = argparse.ArgumentParser(
        description='Visualize peptide intensity, spectral count, and retention time density distributions from FragPipe output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize_peptide_distributions.py --exp_file experiment1/peptide.tsv --exp_psm experiment1/psm.tsv
  python visualize_peptide_distributions.py --exp_file experiment1/peptide.tsv --output_prefix my_experiment --exp_psm experiment1/psm.tsv
        """
    )
    parser.add_argument('--exp_file', required=True,
                       help='Path to peptide.tsv file from FragPipe output')
    parser.add_argument('--output_prefix', default=None,
                       help='Output file prefix (default: derived from input filename)')
    parser.add_argument('--exp_psm', default=None,
                       help='Path to psm.tsv file from FragPipe output (for retention time KDE plot)')
    args = parser.parse_args()
    if not Path(args.exp_file).exists():
        print(f"Error: Input file '{args.exp_file}' does not exist.")
        return 1
    if args.output_prefix is None:
        args.output_prefix = Path(args.exp_file).stem
    try:
        canonical_df, fusion_df = load_and_process_peptide_data(args.exp_file)
        create_distribution_plots(canonical_df, fusion_df, args.output_prefix, psm_file=args.exp_psm)
        create_summary_statistics(canonical_df, fusion_df, args.output_prefix)
        print("\nAnalysis completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main()) 

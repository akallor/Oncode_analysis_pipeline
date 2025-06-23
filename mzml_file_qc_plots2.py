import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyteomics import mzml

# Directory containing mzML files
DATA_DIR = '/content/drive/MyDrive/Utrecht_Oncode_pipeline/'
PLOT_DIR = DATA_DIR  # Save plots in the same directory

# Find all mzML files
mzml_files = sorted(glob.glob(os.path.join(DATA_DIR, '*.mzML')))

# Data storage
replicate_data = {}

print(f"Found {len(mzml_files)} mzML files.")

# Extract m/z, RT, and intensity values from each file
for mzml_file in mzml_files:
    replicate_name = os.path.basename(mzml_file).replace('.mzML', '')
    mzs = []
    rts = []
    intensities = []
    spectra_count = 0
    print(f"Reading {mzml_file} ...")
    with mzml.MzML(mzml_file) as reader:
        for spectrum in reader:
            if spectrum.get('ms level') == 1 or spectrum.get('ms level') == 2:
                mz_array = spectrum.get('m/z array')
                intensity_array = spectrum.get('intensity array')
                rt = spectrum.get('scanList', {}).get('scan', [{}])[0].get('scan start time')
                if mz_array is not None and intensity_array is not None and rt is not None:
                    mzs.extend(mz_array)
                    intensities.extend(intensity_array)
                    rts.extend([rt] * len(mz_array))
                    spectra_count += 1
    replicate_data[replicate_name] = {
        'mz': np.array(mzs),
        'rt': np.array(rts),
        'intensity': np.array(intensities),
        'spectra_count': spectra_count
    }
    print(f"  Extracted {len(mzs)} m/z values, {spectra_count} spectra.")

# Set plot style
sns.set(style='whitegrid', font_scale=1.2)

# Overlayed histograms for m/z
plt.figure(figsize=(10, 6))
for name, data in replicate_data.items():
    plt.hist(data['mz'], bins=200, alpha=0.5, label=name, density=True)
plt.xlabel('m/z')
plt.ylabel('Density')
plt.title('Overlayed m/z Histograms per Replicate')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'mz_hist_overlay.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'mz_hist_overlay.pdf'))
plt.close()

# Overlayed histograms for RT
plt.figure(figsize=(10, 6))
for name, data in replicate_data.items():
    plt.hist(data['rt'], bins=200, alpha=0.5, label=name, density=True)
plt.xlabel('Retention Time (min)')
plt.ylabel('Density')
plt.title('Overlayed RT Histograms per Replicate')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'rt_hist_overlay.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'rt_hist_overlay.pdf'))
plt.close()

# Boxplots for m/z
mz_df = pd.DataFrame({name: data['mz'] for name, data in replicate_data.items()})
mz_df_melt = mz_df.melt(var_name='Replicate', value_name='m/z')
plt.figure(figsize=(10, 6))
sns.boxplot(x='Replicate', y='m/z', data=mz_df_melt)
plt.title('m/z Boxplot per Replicate')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'mz_boxplot.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'mz_boxplot.pdf'))
plt.close()

# Boxplots for RT
rt_df = pd.DataFrame({name: data['rt'] for name, data in replicate_data.items()})
rt_df_melt = rt_df.melt(var_name='Replicate', value_name='RT')
plt.figure(figsize=(10, 6))
sns.boxplot(x='Replicate', y='RT', data=rt_df_melt)
plt.title('RT Boxplot per Replicate')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'rt_boxplot.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'rt_boxplot.pdf'))
plt.close()

# Barplot for spectra count per replicate
plt.figure(figsize=(8, 5))
sns.barplot(x=list(replicate_data.keys()), y=[d['spectra_count'] for d in replicate_data.values()])
plt.title('Total Spectra Count per Replicate')
plt.xlabel('Replicate')
plt.ylabel('Spectra Count')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'spectra_count_barplot.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'spectra_count_barplot.pdf'))
plt.close()

print('All plots saved as PNG (300 dpi) and PDF in:', PLOT_DIR) 

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyteomics import mzml
from pyopenms import MSExperiment, MzMLFile

# Directory containing mzML files
DATA_DIR = '/content/drive/MyDrive/Utrecht_Oncode_pipeline/'
PLOT_DIR = DATA_DIR  # Save plots in the same directory

# Find all mzML files
mzml_files = sorted(glob.glob(os.path.join(DATA_DIR, '*.mzML')))

# Data storage for aggregate plots
replicate_data = {}

print(f"Found {len(mzml_files)} mzML files.")

for mzml_path in mzml_files:
    replicate_name = os.path.basename(mzml_path).replace('.mzML', '')
    print(f"\nQC for: {mzml_path}")
    # --- Per-file QC using pyopenms ---
    exp = MSExperiment()
    MzMLFile().load(mzml_path, exp)
    print(f"  Total spectra: {len(exp)}")
    tic, bpc, rts = [], [], []
    fragment_peaks, ms2_charges = [], []
    all_mz, all_rt = [], []
    empty_spectra = []
    for i, spectrum in enumerate(exp):
        mz, intensity = spectrum.get_peaks()
        if len(mz) == 0:
            empty_spectra.append(i)
        all_mz.extend(mz)
        all_rt.append(spectrum.getRT())
        if spectrum.getMSLevel() == 1:
            if len(intensity) == 0:
                continue
            tic.append(np.sum(intensity))
            bpc.append(np.max(intensity))
            rts.append(spectrum.getRT())
        elif spectrum.getMSLevel() == 2:
            fragment_peaks.append(len(mz))
            precursors = spectrum.getPrecursors()
            if precursors:
                ms2_charges.append(precursors[0].getCharge())
    # TIC/BPC plot
    plt.figure(figsize=(12, 5))
    sns.lineplot(x=rts, y=tic, label='TIC')
    sns.lineplot(x=rts, y=bpc, label='BPC')
    plt.title(f"TIC and BPC ({replicate_name})")
    plt.xlabel("Retention Time (s)")
    plt.ylabel("Intensity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"{replicate_name}_tic_bpc.png"), dpi=300)
    plt.close()
    # MS2 stats
    avg_ms2_peaks = np.mean(fragment_peaks) if fragment_peaks else 0
    ms2_charge_dist = pd.Series(ms2_charges).value_counts().sort_index() if ms2_charges else pd.Series([])
    # m/z and RT range
    mz_min, mz_max = min(all_mz) if all_mz else 0, max(all_mz) if all_mz else 0
    rt_min, rt_max = min(all_rt) if all_rt else 0, max(all_rt) if all_rt else 0
    # Ion mobility check (first 100 scans)
    has_im = 0
    with mzml.read(mzml_path) as reader:
        for i, spec in enumerate(reader):
            if 'inverse reduced ion mobility' in spec.get('scanList', {}).get('scan', [{}])[0]:
                has_im += 1
            if i >= 100:
                break
    # Save per-file summary
    summary_path = os.path.join(PLOT_DIR, f"{replicate_name}_mzml_qc_summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"Total spectra: {len(exp)}\n")
        f.write(f"Avg. MS2 peaks: {avg_ms2_peaks:.2f}\n")
        f.write(f"Empty spectra: {len(empty_spectra)}\n")
        f.write(f"Ion mobility in first 100 scans: {'Yes' if has_im else 'No'}\n")
        f.write(f"m/z range: {mz_min} - {mz_max}\n")
        f.write(f"RT range (s): {rt_min} - {rt_max}\n")
        f.write("Charge state distribution:\n")
        if not ms2_charge_dist.empty:
            for charge, count in ms2_charge_dist.items():
                f.write(f"  z={charge}: {count}\n")
        else:
            f.write("  No MS2 charge data found.\n")
    print(f"  Saved summary to {summary_path}")
    # Store for aggregate plots
    # For aggregate plots, use pyteomics for efficient parsing
    mzs, rts, intensities = [], [], []
    spectra_count = 0
    with mzml.MzML(mzml_path) as reader:
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

# ========== Aggregate Plots ==========

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

# Overlayed histograms for intensity
plt.figure(figsize=(10, 6))
for name, data in replicate_data.items():
    intensity_vals = data['intensity']
    if len(intensity_vals) > 500000:
        intensity_vals = np.random.choice(intensity_vals, 500000, replace=False)
    plt.hist(intensity_vals, bins=200, alpha=0.5, label=name, density=True)
plt.xlabel('Intensity')
plt.ylabel('Density')
plt.title('Overlayed Intensity Histograms per Replicate')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'intensity_hist_overlay.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'intensity_hist_overlay.pdf'))
plt.close()

# Boxplots for m/z (long format, memory efficient)
mz_long = []
for name, data in replicate_data.items():
    mz_vals = data['mz']
    if len(mz_vals) > 500000:
        mz_vals = np.random.choice(mz_vals, 500000, replace=False)
    mz_long.append(pd.DataFrame({'Replicate': name, 'm/z': mz_vals}))
mz_long_df = pd.concat(mz_long, ignore_index=True)
plt.figure(figsize=(10, 6))
sns.boxplot(x='Replicate', y='m/z', data=mz_long_df, showfliers=False)
plt.title('m/z Boxplot per Replicate')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'mz_boxplot.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'mz_boxplot.pdf'))
plt.close()

# Boxplots for RT (long format, memory efficient)
rt_long = []
for name, data in replicate_data.items():
    rt_vals = data['rt']
    if len(rt_vals) > 500000:
        rt_vals = np.random.choice(rt_vals, 500000, replace=False)
    rt_long.append(pd.DataFrame({'Replicate': name, 'RT': rt_vals}))
rt_long_df = pd.concat(rt_long, ignore_index=True)
plt.figure(figsize=(10, 6))
sns.boxplot(x='Replicate', y='RT', data=rt_long_df, showfliers=False)
plt.title('RT Boxplot per Replicate')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'rt_boxplot.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'rt_boxplot.pdf'))
plt.close()

# Boxplots for intensity (long format, memory efficient)
intensity_long = []
for name, data in replicate_data.items():
    intensity_vals = data['intensity']
    if len(intensity_vals) > 500000:
        intensity_vals = np.random.choice(intensity_vals, 500000, replace=False)
    intensity_long.append(pd.DataFrame({'Replicate': name, 'Intensity': intensity_vals}))
intensity_long_df = pd.concat(intensity_long, ignore_index=True)
plt.figure(figsize=(10, 6))
sns.boxplot(x='Replicate', y='Intensity', data=intensity_long_df, showfliers=False)
plt.title('Intensity Boxplot per Replicate')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'intensity_boxplot.png'), dpi=300)
plt.savefig(os.path.join(PLOT_DIR, 'intensity_boxplot.pdf'))
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

print('All plots and summaries saved as PNG (300 dpi), PDF, and TXT in:', PLOT_DIR) 

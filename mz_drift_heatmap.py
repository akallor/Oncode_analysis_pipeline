import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Try to import alphatims and pyteomics
try:
    from alphatims.bruker import TimsTOF
except ImportError:
    TimsTOF = None
try:
    from pyteomics import mzml
except ImportError:
    mzml = None

DATA_DIR = '/content/drive/MyDrive/Utrecht_Oncode_pipeline/'
PLOT_DIR = DATA_DIR

def process_tdf(tdf_path):
    dataset = TimsTOF(str(tdf_path))
    df = dataset.as_dataframe(['mz', 'inv_ion_mobility', 'intensity'])
    df = df[df['inv_ion_mobility'] > 0]
    df['drift_time'] = 1 / df['inv_ion_mobility']
    return df

def process_mzml(mzml_path):
    mzs, drift_times, intensities = [], [], []
    with mzml.MzML(mzml_path) as reader:
        for spectrum in reader:
            mz_array = spectrum.get('m/z array')
            intensity_array = spectrum.get('intensity array')
            scan = spectrum.get('scanList', {}).get('scan', [{}])[0]
            drift_time = scan.get('inverse reduced ion mobility')
            if mz_array is not None and intensity_array is not None and drift_time is not None:
                drift_time = 1 / drift_time if drift_time > 0 else np.nan
                mzs.extend(mz_array)
                drift_times.extend([drift_time] * len(mz_array))
                intensities.extend(intensity_array)
    return np.array(mzs), np.array(drift_times), np.array(intensities)

def plot_heatmap(mz, drift_time, intensity, fname, annotate_n=10):
    plt.figure(figsize=(12, 6))
    hb = plt.hexbin(mz, drift_time, C=intensity, gridsize=200, reduce_C_function=np.sum, cmap='cool')
    plt.colorbar(hb, label='Summed Intensity')
    plt.xlabel('m/z')
    plt.ylabel('Drift time (ms)')
    plt.title(f'm/z vs Drift Time Heatmap\n{fname}')

    # Annotate ions with greatest drift time and m/z
    idx_drift = np.argsort(drift_time)[-annotate_n:]
    idx_mz = np.argsort(mz)[-annotate_n:]
    for idx in np.unique(np.concatenate([idx_drift, idx_mz])):
        plt.scatter(mz[idx], drift_time[idx], color='red', s=30, edgecolor='black', zorder=3)
        plt.text(mz[idx], drift_time[idx], f"{int(mz[idx])},{drift_time[idx]:.2f}", color='red', fontsize=8)

    plt.tight_layout()
    outpath = os.path.join(PLOT_DIR, f"{fname}_mz_vs_drift_heatmap.png")
    plt.savefig(outpath, dpi=300)
    plt.close()
    print(f"Saved plot: {outpath}")

def main():
    files = glob.glob(os.path.join(DATA_DIR, '*.d')) + glob.glob(os.path.join(DATA_DIR, '*.mzML'))
    for f in files:
        fname = os.path.basename(f).replace('.d', '').replace('.mzML', '')
        print(f"Processing: {f}")
        if f.endswith('.d') and TimsTOF is not None:
            df = process_tdf(f)
            mz, drift_time, intensity = df['mz'].values, df['drift_time'].values, df['intensity'].values
        elif f.endswith('.mzML') and mzml is not None:
            mz, drift_time, intensity = process_mzml(f)
        else:
            print(f"Skipping {f} (unsupported or missing library)")
            continue
        # Remove NaNs and zeros
        mask = (~np.isnan(mz)) & (~np.isnan(drift_time)) & (intensity > 0)
        mz, drift_time, intensity = mz[mask], drift_time[mask], intensity[mask]
        if len(mz) == 0:
            print(f"No valid data in {f}")
            continue
        plot_heatmap(mz, drift_time, intensity, fname)

if __name__ == '__main__':
    main() 

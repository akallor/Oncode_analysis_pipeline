#QC for raw data (.tdf files)
from alphatims.bruker import TimsTOF
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

raw_data_dir = Path("/content/drive/MyDrive/Utrecht_Oncode_pipeline/")
qc_dir = raw_data_dir / "tdf_qc"
qc_dir.mkdir(exist_ok=True)

d_folders = sorted(raw_data_dir.glob("*.d"))

for d_folder in d_folders:
    print(f"Processing: {d_folder}")
    dataset = TimsTOF(str(d_folder))
    frames = dataset.frames
    print(frames.columns)
    for col in frames.columns:
        if 'type' in col.lower():
            print(f"Using column: {col}")
            ms_type_col = col
            break
    else:
        raise ValueError("No MS type column found in frames DataFrame!")
    # Frame metadata
    print(f"  Total number of frames: {len(frames)}")
    print(f"  MS1 scans: {sum(frames[ms_type_col] == 0)}")
    print(f"  MS2 scans: {sum(frames[ms_type_col] == 8)}")

    # TIC and BPC plots using intensity_values and NumPeaks
    num_peaks = frames['NumPeaks'].values
    intensity_values = dataset.intensity_values
    split_indices = np.cumsum(num_peaks)[:-1]
    intensity_per_frame = np.split(intensity_values, split_indices)
    tic = np.array([arr.sum() for arr in intensity_per_frame])
    bpc = np.array([arr.max() if len(arr) > 0 else 0 for arr in intensity_per_frame])

    plt.figure(figsize=(12, 5))
    sns.lineplot(x=frames['Id'], y=tic, label='TIC')
    sns.lineplot(x=frames['Id'], y=bpc, label='BPC')
    plt.title(f"TIC and BPC Chromatogram\n{d_folder.name}")
    plt.xlabel("Frame Index")
    plt.ylabel("Intensity")
    plt.legend()
    plt.tight_layout()
    plot_path = qc_dir / f"{d_folder.name}_tic_bpc.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"  Saved TIC/BPC plot to {plot_path}")

    # Low signal frames
    low_signal_frames = tic[tic < np.median(tic) * 0.2]
    print(f"  Frames with low signal: {len(low_signal_frames)}")

    # m/z and ion mobility range
    mz_min, mz_max = dataset.mz_min_value, dataset.mz_max_value
    mob_min, mob_max = dataset.mobility_min_value, dataset.mobility_max_value
    print(f"  m/z range: {mz_min} to {mz_max}")
    print(f"  Inv. ion mobility range: {mob_min} to {mob_max}")

    # Save summary
    summary_path = qc_dir / f"{d_folder.name}_qc_summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Total frames: {len(frames)}\n")
        f.write(f"MS1 scans: {sum(frames[ms_type_col] == 0)}\n")
        f.write(f"MS2 scans: {sum(frames[ms_type_col] == 8)}\n")
        f.write(f"Low signal frames: {len(low_signal_frames)}\n")
        f.write(f"m/z range: {mz_min} - {mz_max}\n")
        f.write(f"Ion mobility range: {mob_min} - {mob_max}\n")
    print(f"  Saved summary to {summary_path}\n") 

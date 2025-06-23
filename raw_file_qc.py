# ==========================
# QC SCRIPT 1: RAW .TDF FILE QC
# ==========================

# File: qc_raw_tdf.py

import alphatims
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

raw_data_dir = Path("/content/my_raw_tims_data")  # Change this path accordingly
dataset = alphatims.bruker.TimsTOFDataset(str(raw_data_dir))

# Frame metadata
print(f"Total number of frames: {len(dataset.frames)}")
print(f"MS1 scans: {sum(dataset.frames.ms_type == 0)}")
print(f"MS2 scans: {sum(dataset.frames.ms_type == 8)}")

# TIC and BPC plots
intensities = dataset.intensity()
tic = intensities.groupby("frame").intensity.sum()
bpc = intensities.groupby("frame").intensity.max()

plt.figure(figsize=(12, 5))
sns.lineplot(x=tic.index, y=tic.values, label='TIC')
sns.lineplot(x=bpc.index, y=bpc.values, label='BPC')
plt.title("TIC and BPC Chromatogram")
plt.xlabel("Frame Index")
plt.ylabel("Intensity")
plt.legend()
plt.tight_layout()
plt.savefig("tdf_tic_bpc.png")

# Low signal frames
low_signal_frames = tic[tic < tic.median() * 0.2]
print(f"Frames with low signal: {len(low_signal_frames)}")

# m/z and ion mobility range
print(f"m/z range: {dataset.mz().min()} to {dataset.mz().max()}")
print(f"Inv. ion mobility range: {dataset.inv_ion_mobility().min()} to {dataset.inv_ion_mobility().max()}")

# Save summary
with open("raw_tdf_qc_summary.txt", "w") as f:
    f.write(f"Total frames: {len(dataset.frames)}\n")
    f.write(f"MS1 scans: {sum(dataset.frames.ms_type == 0)}\n")
    f.write(f"MS2 scans: {sum(dataset.frames.ms_type == 8)}\n")
    f.write(f"Low signal frames: {len(low_signal_frames)}\n")
    f.write(f"m/z range: {dataset.mz().min()} - {dataset.mz().max()}\n")
    f.write(f"Ion mobility range: {dataset.inv_ion_mobility().min()} - {dataset.inv_ion_mobility().max()}\n")

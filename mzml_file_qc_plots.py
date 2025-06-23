# =============================
# QC SCRIPT 2: mzML QC Pipeline
# =============================

# File: qc_mzml.py

from pyopenms import MSExperiment, MzMLFile
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pyteomics import mzml

mzml_path = "/content/converted.mzML"  # Change this as needed
exp = MSExperiment()
MzMLFile().load(mzml_path, exp)

print(f"Total spectra: {len(exp)}")

tic, bpc, rts = [], [], []

for spectrum in exp:
    if spectrum.getMSLevel() == 1:
        mz, intensity = spectrum.get_peaks()
        if len(intensity) == 0:
            continue
        tic.append(np.sum(intensity))
        bpc.append(np.max(intensity))
        rts.append(spectrum.getRT())

plt.figure(figsize=(12, 5))
sns.lineplot(x=rts, y=tic, label='TIC')
sns.lineplot(x=rts, y=bpc, label='BPC')
plt.title("TIC and BPC (mzML)")
plt.xlabel("Retention Time (s)")
plt.ylabel("Intensity")
plt.legend()
plt.tight_layout()
plt.savefig("mzml_tic_bpc.png")

fragment_peaks, ms2_charges = [], []

for spectrum in exp:
    if spectrum.getMSLevel() == 2:
        mz, intensity = spectrum.get_peaks()
        fragment_peaks.append(len(mz))
        precursors = spectrum.getPrecursors()
        if precursors:
            ms2_charges.append(precursors[0].getCharge())

print(f"Avg. MS2 peaks: {np.mean(fragment_peaks):.2f}")
print("Charge state distribution:")
print(pd.Series(ms2_charges).value_counts().sort_index())

all_mz, all_rt = [], []

for spectrum in exp:
    mz, intensity = spectrum.get_peaks()
    all_mz.extend(mz)
    all_rt.append(spectrum.getRT())

print(f"m/z range: {min(all_mz):.2f} - {max(all_mz):.2f}")
print(f"RT range (min): {min(all_rt)/60:.2f} - {max(all_rt)/60:.2f}")

# Ion mobility check (first 100 scans)
has_im = 0
with mzml.read(mzml_path) as reader:
    for i, spec in enumerate(reader):
        if 'inverse reduced ion mobility' in spec.get('scanList', {}).get('scan', [{}])[0]:
            has_im += 1
        if i >= 100:
            break

print(f"Ion mobility present in first 100 scans: {'Yes' if has_im else 'No'}")

# Empty spectra check
empty_spectra = [i for i, s in enumerate(exp) if len(s.get_peaks()[0]) == 0]
print(f"Empty or zero-intensity spectra: {len(empty_spectra)}")

# Save summary
with open("mzml_qc_summary.txt", "w") as f:
    f.write(f"Total spectra: {len(exp)}\n")
    f.write(f"Avg. MS2 peaks: {np.mean(fragment_peaks):.2f}\n")
    f.write(f"Empty spectra: {len(empty_spectra)}\n")
    f.write(f"Ion mobility in first 100 scans: {'Yes' if has_im else 'No'}\n")
    f.write(f"m/z range: {min(all_mz)} - {max(all_mz)}\n")
    f.write(f"RT range (s): {min(all_rt)} - {max(all_rt)}\n")

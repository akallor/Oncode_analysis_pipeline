# Oncode_analysis_pipeline
Developing a comprehensive immunopeptidomics mass spectrometry analysis pipeline for Oncode Demonstrator Project WP2 (&amp; possibly WP3)
#Objectives: 
a) QC/clean immunopeptidomics raw data from TIMSTOF experiments.
b) The cleaned data is then converted to a compatible mzML format and analyzed by either Fragpipe or combining Fragpipe, Peaks, Maxquant etc.
c) The spectra are rescored through Prosit to improve accuracy.
d) Collision cross section is calculated through the model of choice (Prosit or our own CCS prediction model).
e) Retention time is predicted for the non-canonical peptides derived from fusion events (just like the CCS itself).
f) Binding affinity analysis is conducted on all presented immunopeptides based on the patient's haplotype.
g) Codon usage/translation initiation site prediction for novel orfs/non-canonical immunopeptides.
h) Finally, similarity to known MHC ligands and epitopes (mined from CEDAR & IEDB databases) is computed.
i) The final list of peptides based on all the criteria above are prepared and a ranking is done.

How to run the codes (in order):
conda_install.py --> create_timstof_env.py --> run_timsconvert.py --> mzml_quality_check.py

The downstream objectives of this pipeline are to build a comprehensive log-odds method for antigen prioritization based on several physicochemical features, including binding affinity as shown below:


<img width="475" height="285" alt="image" src="https://github.com/user-attachments/assets/5dca4498-ee94-401a-acbf-05d9998b727e" />

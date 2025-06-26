import os
import glob
import argparse
import re


def extract_sample_name(filename):
    # Remove extension and look for 'Rep' or 'rep' followed by a number
    base = os.path.basename(filename)
    # Remove .mzML or other extensions
    base = re.sub(r'\.[^.]+$', '', base)
    # Remove _RepN or _repN or -RepN or -repN
    sample = re.sub(r'([_-])?[Rr]ep\d+$', '', base)
    return sample


def main():
    parser = argparse.ArgumentParser(description='Prepare FragPipe manifest file.')
    parser.add_argument('--data_dir', required=True, help='Path to directory containing mzML files')
    parser.add_argument('--data_type', required=True, help='Data type (e.g., DDA, DIA, GPF-DIA, DIA-Quant, DIA-Lib)')
    parser.add_argument('--study_id', required=True, help='Study ID for output manifest file')
    args = parser.parse_args()

    mzml_files = sorted(glob.glob(os.path.join(args.data_dir, '*.mzML')))
    if not mzml_files:
        print('No mzML files found in the specified directory.')
        return

    # Group files by sample name (excluding replicate info)
    sample_to_files = {}
    for f in mzml_files:
        sample = extract_sample_name(f)
        sample_to_files.setdefault(sample, []).append(f)

    # Prepare manifest rows
    rows = []
    for sample, files in sample_to_files.items():
        # Sort files for consistent replicate assignment
        files_sorted = sorted(files)
        for idx, f in enumerate(files_sorted, 1):
            rows.append([f, 'exp', str(idx), args.data_type])

    # Write to manifest file
    manifest_path = f"{args.study_id}_manifest.tsv"
    with open(manifest_path, 'w') as out:
        for row in rows:
            out.write('\t'.join(row) + '\n')
    print(f"Manifest file written to {manifest_path}")

if __name__ == '__main__':
    main() 

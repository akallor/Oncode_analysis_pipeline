import os
import glob
import argparse


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

    # Prepare manifest rows: assign replicate numbers in order
    rows = []
    for idx, f in enumerate(mzml_files, 1):
        rows.append([f, 'exp', str(idx), args.data_type])

    # Write to manifest file in the specified directory
    manifest_path = os.path.join(args.data_dir, f"{args.study_id}_manifest.tsv")
    with open(manifest_path, 'w') as out:
        for row in rows:
            out.write('\t'.join(row) + '\n')
    print(f"Manifest file written to {manifest_path}")

if __name__ == '__main__':
    main() 

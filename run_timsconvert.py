import os
import glob
import subprocess

#Path to the timsconvert executable in the conda environment created by the other script.
TIMSCONVERT_EXECUTABLE = '/usr/local/envs/timsconvert_env/bin/timsconvert'

def find_data_directories(base_path):
    """
    Recursively find all directories containing an 'analysis.tdf' file.
    """
    found_dirs = []
    print(f"Searching for 'analysis.tdf' files recursively under {base_path}...")
    for root, dirs, files in os.walk(base_path):
        if 'analysis.tdf' in files:
            # The 'root' is the directory containing 'analysis.tdf', which is the .d folder.
            found_dirs.append(root)
    return found_dirs

def convert_to_mzml(input_dir, output_dir):
    """
    Convert a .d directory to a .mzML file using timsconvert.
    """
    #Check if the primary TDF file exists.
    if not os.path.exists(os.path.join(input_dir, 'analysis.tdf')):
        print(f"Skipping {input_dir}, as it does not contain analysis.tdf")
        return

    #Create a name for the output file based on the input directory name to check for existence.
    output_filename = os.path.basename(os.path.normpath(input_dir)).replace('.d', '.mzML')
    output_path = os.path.join(output_dir, output_filename)

    #To avoid re-running conversions, we can check if the output file already exists.
    if os.path.exists(output_path):
        print(f"Skipping conversion for {input_dir}, output file {output_path} already exists.")
        return

    #Command to execute timsconvert with user-specified options.
    #Note: --input expects the .d directory.
    command = [
        TIMSCONVERT_EXECUTABLE,
        '--input', input_dir,
        '--outdir', output_dir,
        '--mode', 'centroid',
        '--use_raw_calibration',
        '--verbose',
    ]

    print(f"Converting {input_dir}...")
    try:
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Conversion process finished.")
        if result.stdout:
            print("--- stdout ---")
            print(result.stdout)
        if result.stderr:
            print("--- stderr (verbose output) ---")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting {input_dir}:")
        print(e.stdout)
        print(e.stderr)
    except FileNotFoundError:
        print(f"\nError: '{TIMSCONVERT_EXECUTABLE}' not found.")
        print("Please ensure that the 'prepare_n_test_timsconvert_env.py' script has been run successfully,")
        print("which creates the environment at '/usr/local/envs/timsconvert_env'.")
        # Stop the script if timsconvert is not found.
        exit()


def main():
    """
    Main function to orchestrate the file conversion process.
    """
    #Data directory location.
    base_path = '/content/drive/MyDrive/Utrecht_Oncode_pipeline'
    
    output_dir = base_path
    if not os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' does not exist.")
        print("Please ensure your Google Drive is mounted and the path is correct.")
        return

    #Find all directories that contain an 'analysis.tdf' file.
    data_dirs = find_data_directories(base_path)

    if not data_dirs:
        print("No directories containing 'analysis.tdf' were found.")
        print(f"Please check that the 'base_path' variable is set correctly in the script.")
        print(f"Searched within: {base_path}")
        return

    print(f"Found {len(data_dirs)} data directories to process:")
    for d in sorted(data_dirs):
        print(f"  - {d}")

    #Loop through each directory and run the conversion.
    for d in sorted(data_dirs):
        convert_to_mzml(d, output_dir)
        
    print("\nAll conversions have been processed.")

if __name__ == '__main__':
    # further processing after conversion.
    main() 

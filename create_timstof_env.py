#Test creation of timsconvert environment:

import os
import subprocess
import sys
import shutil

try:
    from google.colab import drive
    # Mount Google Drive
    drive.mount('/content/drive')
except ImportError:
    print("This script is designed to run in Google Colab. 'google.colab' not found.")
    print("Skipping Drive mount and environment caching.")
    drive = None


# --- Part 1: Setup and Environment Management ---

# Define paths
drive_env_path = '/content/drive/MyDrive/colab_envs/timsconvert_env'
# The conda create command in Colab with -n will place it here.
# If you use --prefix, you can specify a different location.
local_env_path = '/usr/local/envs/timsconvert_env' 
os.makedirs(local_env_path, exist_ok=True) # Ensure base directory exists

python_executable = os.path.join(local_env_path, 'bin/python')
timsconvert_executable = os.path.join(local_env_path, 'bin/timsconvert')

def check_environment_exists():
    """Check if environment already exists locally"""
    return os.path.exists(python_executable)

def restore_from_drive():
    """Restore environment from Google Drive"""
    if drive and os.path.exists(drive_env_path):
        print("Restoring environment from Google Drive...")
        # Use dirs_exist_ok=True for Python 3.8+
        shutil.copytree(drive_env_path, local_env_path, dirs_exist_ok=True)
        print("Environment restored from Google Drive!")
        return True
    return False

def save_to_drive():
    """Save environment to Google Drive"""
    if drive and os.path.exists(local_env_path):
        print("Saving environment to Google Drive...")
        os.makedirs(os.path.dirname(drive_env_path), exist_ok=True)
        if os.path.exists(drive_env_path):
            shutil.rmtree(drive_env_path)
        shutil.copytree(local_env_path, drive_env_path)
        print("Environment saved to Google Drive!")

# --- Part 2: Create or Restore Environment ---

if check_environment_exists():
    print("Environment already exists locally. Skipping creation.")
elif restore_from_drive():
    print("Environment restored from Google Drive.")
else:
    print("Creating new environment from scratch...")
    
    # 1. Create a virtual environment
    # Using --prefix to ensure the environment is created at local_env_path
    print(f"Step 1: Creating conda environment at '{local_env_path}' with Python 3.10...")
    create_env_command = ["conda", "create", "--prefix", local_env_path, "python=3.10", "-y"]
    process = subprocess.run(create_env_command, capture_output=True, text=True)
    print(process.stdout)
    print(process.stderr)
    if process.returncode != 0:
        print("Error creating conda environment. Exiting.")
        sys.exit(1)
    print("Conda environment created.")

    # 3. Install timsconvert and dependencies
    print("\nStep 3: Installing timsconvert and dependencies using pip within the virtual environment.")
    install_timsconvert_command = [python_executable, "-m", "pip", "install", "git+https://github.com/gtluu/timsconvert"]
    process = subprocess.run(install_timsconvert_command, capture_output=True, text=True)
    print(process.stdout)
    print(process.stderr)
    if process.returncode != 0:
        print("Error installing timsconvert. Exiting.")
        sys.exit(1)
    print("timsconvert and dependencies installed.")

    # Save to Drive after creation
    save_to_drive()

print("\n--- Part 3: Environment Verification and Testing ---")
print("Environment ready for use!")

# 2. Activate the virtual environment (by using full path to python)
print(f"\nVerifying Python version in {python_executable}...")
version_command = [python_executable, "--version"]
process = subprocess.run(version_command, capture_output=True, text=True)
print(process.stdout)
print(process.stderr)
if process.returncode != 0:
    print("Error verifying python version in new environment. Exiting.")
    sys.exit(1)
print("Python version verified.")

# Verify installation
print("\nVerifying installation...")
list_packages_command = [python_executable, "-m", "pip", "list"]
process = subprocess.run(list_packages_command, capture_output=True, text=True)
print(process.stdout)
print(process.stderr)
print("Installation verified.")

# 4. Set the QT_QPA_PLATFORM environment variable
print("\nStep 4: Setting QT_QPA_PLATFORM environment variable to 'offscreen'.")
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
print(f"QT_QPA_PLATFORM is set to: {os.environ.get('QT_QPA_PLATFORM')}")

# 5. Test timsconvert
print("\nStep 5: Testing timsconvert --help.")
test_timsconvert_command = [timsconvert_executable, "--help"]
process = subprocess.run(test_timsconvert_command, capture_output=True, text=True)
print(process.stdout)
print(process.stderr)

if process.returncode == 0:
    print("\ntimsconvert ran successfully within the virtual environment.")
    print("Summary: timsconvert appears to be runnable in the 'timsconvert_env' environment.")
else:
    print("\nError running timsconvert within the virtual environment.")
    print("Summary: timsconvert encountered an error in the 'timsconvert_env' environment.")
    print("Check the output above for details.")

# 6. Finish task
print("\nTask finished.") 

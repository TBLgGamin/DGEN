import sys
import subprocess
import os
import platform
import hashlib
import re
import importlib
from typing import List, Tuple

HASH_FILE = ".install_script_hash"

def check_python_installation() -> bool:
    """Check if Python is installed and accessible."""
    try:
        subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_python_download_instructions() -> str:
    """Get instructions for downloading Python based on the operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "Download Python from https://www.python.org/downloads/windows/"
    elif system == "darwin":
        return "Download Python from https://www.python.org/downloads/mac-osx/"
    elif system == "linux":
        return "Use your distribution's package manager to install Python, or visit https://www.python.org/downloads/source/"
    else:
        return "Visit https://www.python.org/downloads/ to download Python for your operating system."

def read_requirements(file_path: str) -> List[str]:
    """Safely read the requirements file."""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except IOError as e:
        print(f"Error reading requirements file: {e}")
        return []

def validate_package_name(package: str) -> bool:
    """Validate package name to prevent arbitrary code execution."""
    return bool(re.match(r'^[a-zA-Z0-9_.-]+([<>=!]=?[a-zA-Z0-9_.-]+)?$', package))

def install_package(package: str) -> Tuple[bool, str]:
    """Install a single package using pip."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def uninstall_package(package: str) -> None:
    """Uninstall a single package using pip."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package], 
                       check=True, capture_output=True)
        print(f"Uninstalled {package}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to uninstall {package}: {e}")

def verify_installation(package: str) -> bool:
    """Verify that a package was successfully installed."""
    package_name = package.split('==')[0]
    try:
        # First, try to import the package directly
        importlib.import_module(package_name)
        return True
    except ImportError:
        # If direct import fails, try common variations
        variations = [
            package_name.replace('-', '_'),  # Replace hyphens with underscores
            package_name.split('-')[-1],     # Try the last part of the name
            ''.join(part for part in package_name.split('-'))  # Remove hyphens entirely
        ]
        for variation in variations:
            try:
                importlib.import_module(variation)
                return True
            except ImportError:
                continue
    
    # If all attempts fail, try pip show as a last resort
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], 
                                check=True, capture_output=True, text=True)
        return "Version:" in result.stdout
    except subprocess.CalledProcessError:
        return False

def calculate_file_hash(file_path: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_script_hash(hash_value: str) -> None:
    """Save the script's hash to a file."""
    with open(HASH_FILE, 'w') as f:
        f.write(hash_value)

def load_script_hash() -> str:
    """Load the script's hash from a file."""
    try:
        with open(HASH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def self_check() -> bool:
    """Perform a self-check of the script."""
    current_hash = calculate_file_hash(__file__)
    saved_hash = load_script_hash()
    
    if not saved_hash:
        print("This appears to be the first run of the script.")
        save_script_hash(current_hash)
        return True
    
    if current_hash != saved_hash:
        print("Warning: The script has been modified since it was last run.")
        user_input = input("Do you want to continue anyway? (y/n): ").lower()
        if user_input == 'y':
            save_script_hash(current_hash)
            return True
        return False
    
    return True

def main():
    if not self_check():
        print("Exiting for security reasons.")
        return

    if not check_python_installation():
        print("Error: Python is not installed or not accessible.")
        print(get_python_download_instructions())
        return

    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found in the current directory.")
        return

    requirements = read_requirements(requirements_file)
    if not requirements:
        print("No packages to install.")
        return

    print("Installing packages...")
    installed_packages = []
    for package in requirements:
        if not validate_package_name(package):
            print(f"Invalid package name: {package}. Skipping.")
            continue

        success, output = install_package(package)
        if success:
            print(f"Successfully installed {package}")
            if verify_installation(package):
                print(f"Verified installation of {package}")
                installed_packages.append(package)
            else:
                print(f"Warning: Failed to verify installation of {package}")
                print("The package may still be installed correctly. Please check manually.")
        else:
            print(f"Failed to install {package}")
            print(f"Error: {output}")
            rollback = input("Do you want to roll back the installations? (y/n): ").lower() == 'y'
            if rollback:
                for installed_package in installed_packages:
                    uninstall_package(installed_package)
                print("Rolled back installations.")
                return

    print("Installation process completed.")
    print("The hash file is to check if the install script hasn't been modified to prevent malicious use of the install script from the user or external parties.")

if __name__ == "__main__":
    main()
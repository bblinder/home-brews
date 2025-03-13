#!/usr/bin/env bash

# Bootstrap and setup a Python virtual environment and install required packages.

set -Eeuo pipefail
trap 'echo -e "${RED}Error at line $LINENO${NOFORMAT}" >&2' ERR

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
venv_dir="${script_dir}/venv"

# Setup colors
setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
  else
    NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
  fi
}

# Display help message
show_help() {
    echo "Usage: $0 [option...]"
    echo "Bootstraps a virtual environment and installs/updates required packages."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message and exit"
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option: $1${NOFORMAT}"
            show_help
            exit 1
            ;;
    esac
    shift
done

setup_colors

# Create the virtual environment if it doesn't exist
if [[ ! -d "$venv_dir" ]]; then
    echo -e "${GREEN}Creating virtual environment at $venv_dir...${NOFORMAT}"
    python3 -m venv "$venv_dir"
fi

# Check for requirements.txt and install packages
if [[ -f "$script_dir/requirements.txt" ]]; then
    echo -e "${CYAN}Installing required packages from requirements.txt...${NOFORMAT}"
    "$venv_dir/bin/pip" install --upgrade -r "$script_dir/requirements.txt"
else
    echo -e "${YELLOW}requirements.txt file not found. Skipping package installation.${NOFORMAT}"
fi

# Final instructions for activating the virtual environment
activation_instructions() {
    echo -e "${PURPLE}To activate the virtual environment, run:${NOFORMAT}"
    echo -e "${GREEN}source ${venv_dir}/bin/activate${NOFORMAT}"
}

# Instructions for deactivating the virtual environment when done
deactivation_instructions() {
    echo -e "${PURPLE}To deactivate the virtual environment when finished, run:${NOFORMAT}"
    echo -e "${GREEN}deactivate${NOFORMAT}"
}

# Main script operations
main() {
    # Placeholder for main script operations
    echo -e "${CYAN}Setting up your Python virtual environment...${NOFORMAT}"
    # The actual operations like environment setup and package installation are performed here
}

main "$@"
activation_instructions
echo ""
deactivation_instructions

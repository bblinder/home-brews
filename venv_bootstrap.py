# venv_bootstrap.py

import os
import subprocess
import sys


def bootstrap_venv(venv_dir="venv", requirements_file="requirements.txt"):
    """Bootstraps a Python virtual environment.

    Args:
        venv_dir (str): The directory of the virtual environment. Defaults to 'venv'.
        requirements_file (str): Path to a requirements.txt file. Defaults to 'requirements.txt'.
    """
    SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
    VENV_DIR = os.path.join(SCRIPT_DIR, venv_dir)
    IS_WINDOWS = sys.platform.startswith("win")
    VENV_BIN_DIR = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin")
    VENV_ACTIVATE_BASH = os.path.join(VENV_BIN_DIR, "activate")
    REQUIREMENTS_PATH = os.path.join(SCRIPT_DIR, requirements_file)
    PYTHON_EXECUTABLE = os.path.join(
        VENV_BIN_DIR, "python3.exe" if IS_WINDOWS else "python3"
    )

    if not os.path.exists(VENV_DIR):
        print("No virtual environment found. Setting one up...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print("Virtual environment created at {}".format(VENV_DIR))

    if "VIRTUAL_ENV" not in os.environ:
        if IS_WINDOWS:
            command = '"{}" && "{}" "{}" {}'.format(
                VENV_ACTIVATE_BASH, PYTHON_EXECUTABLE, __file__, " ".join(sys.argv[1:])
            )
            subprocess.check_call(command, shell=True)
        else:
            command = 'source "{}" && "{}" "{}" {}'.format(
                VENV_ACTIVATE_BASH,
                PYTHON_EXECUTABLE,
                __file__,
                " ".join(map(lambda x: '"{}"'.format(x), sys.argv[1:])),
            )
            os.execle("/bin/bash", "bash", "-c", command, os.environ)
        sys.exit()
    else:
        if os.path.exists(REQUIREMENTS_PATH):
            print("Installing dependencies from requirements.txt...")
            subprocess.check_call(
                [
                    PYTHON_EXECUTABLE,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    REQUIREMENTS_PATH,
                    "--upgrade",
                ],
                cwd=SCRIPT_DIR,
            )
        else:
            print("requirements.txt not found, skipping dependency installation.")

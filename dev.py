#!/usr/bin/env python
"""
Development helper script for Python Manager
This script helps set up the development environment and run linting checks.
"""

import argparse
import os
import subprocess
import sys


def run_command(command, capture_output=False):
    """Run a shell command and optionally capture its output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        if capture_output:
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
        sys.exit(result.returncode)
    return result


def setup_environment():
    """Setup virtual environment and install dependencies"""
    if not os.path.exists("venv"):
        print("Setting up virtual environment...")
        run_command("python -m venv venv")

    # Activate venv and install requirements
    if os.name == "nt":  # Windows
        pip_cmd = r"venv\Scripts\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"

    run_command(f"{pip_cmd} install --upgrade pip")
    run_command(f"{pip_cmd} install -r requirements.txt")
    run_command(f"{pip_cmd} install pylint pytest coverage")

    print("Environment setup complete!")


def run_pylint():
    """Run pylint on the project files"""
    print("Running Pylint on project files...")

    # Determine the proper Python executable based on the OS
    if os.name == "nt":  # Windows
        pylint_cmd = r"venv\Scripts\pylint"
    else:  # Unix/Linux/Mac
        pylint_cmd = "venv/bin/pylint"

    # Run pylint excluding migrations and __pycache__ directories
    command = f"{pylint_cmd} "

    # Build list of Python files, excluding migrations and __pycache__
    python_files = []

    for root, _, files in os.walk("."):
        if "migrations" in root or "__pycache__" in root or "venv" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    if not python_files:
        print("No Python files found to lint")
        return 0

    # Run pylint on all Python files
    command += " ".join(python_files)
    result = run_command(command, capture_output=True)

    print(result.stdout)
    return result.returncode


def run_tests():
    """Run the project's test suite"""
    print("Running tests...")
    # Determine the proper Python executable based on the OS
    if os.name == "nt":  # Windows
        pytest_cmd = r"venv\Scripts\pytest"
    else:  # Unix/Linux/Mac
        pytest_cmd = "venv/bin/pytest"

    run_command(f"{pytest_cmd} -v")


def main():
    parser = argparse.ArgumentParser(description="Development helper for Python Manager")
    parser.add_argument("--setup", action="store_true", help="Setup development environment")
    parser.add_argument("--lint", action="store_true", help="Run pylint")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--all", action="store_true", help="Run setup, lint, and tests")

    args = parser.parse_args()

    if args.all or (not args.setup and not args.lint and not args.test):
        setup_environment()
        run_pylint()
        run_tests()
    else:
        if args.setup:
            setup_environment()
        if args.lint:
            run_pylint()
        if args.test:
            run_tests()

    print("All tasks completed!")


if __name__ == "__main__":
    main()

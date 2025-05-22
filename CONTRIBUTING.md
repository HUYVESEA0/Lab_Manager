# Contributing to Python Manager

Thank you for considering contributing to Python Manager! This document outlines the process and standards for contributing to this project.

## Development Setup

1. Clone the repository and set up your environment:

```bash
git clone [repository-url]
cd Lab_Manager-1
python -m venv venv

# On Windows
venv\Scripts\activate
# On Unix/Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
pip install pre-commit pylint pytest
```

2. Set up pre-commit hooks:

```bash
pre-commit install
```

3. Run the development helper script:

```bash
# Run all tasks (setup, lint, test)
python dev.py --all

# Or run specific tasks
python dev.py --lint  # Run only linting
python dev.py --test  # Run only tests
```

## Code Style and Standards

This project uses:
- **Pylint** for static code analysis
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for style guide enforcement

The configuration for these tools is in:
- `.pylintrc` for Pylint
- `.pre-commit-config.yaml` for pre-commit hooks

## Pull Request Process

1. Ensure your code passes all linting checks and tests.
2. Update documentation as necessary.
3. Make sure your commit messages are clear and descriptive.
4. Submit a pull request with a clear description of the changes.

## GitHub Actions

This project uses GitHub Actions for continuous integration:
- The `pylint.yml` workflow runs on each push and pull request.
- It checks the code with Pylint on multiple Python versions.

## Reporting Issues

If you find bugs or have feature requests, please open an issue on the GitHub repository.

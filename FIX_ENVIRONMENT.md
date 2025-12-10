# How to Fix the ModuleNotFoundError

## Problem
You're getting `ModuleNotFoundError: No module named 'numpy'` because:
1. The virtual environment references Python 3.14 which doesn't exist on your system
2. Dependencies aren't installed

## Solution Options

### Option 1: Recreate Virtual Environment (Recommended)

1. **Delete the old virtual environment:**
   ```powershell
   Remove-Item -Recurse -Force spacyenv
   ```

2. **Find your Python installation:**
   ```powershell
   # Try these commands to find Python:
   python --version
   python3 --version
   py --version
   py -3 --version
   ```

3. **Create a new virtual environment:**
   ```powershell
   # Use whichever Python command worked above
   python -m venv spacyenv
   # OR
   py -3 -m venv spacyenv
   ```

4. **Activate the virtual environment:**
   ```powershell
   .\spacyenv\Scripts\activate
   ```

5. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### Option 2: Install Dependencies Globally (Not Recommended)

If you can't fix the virtual environment, you can install packages globally:

```powershell
# Find Python first
python -m pip install -r requirements.txt
# OR
py -3 -m pip install -r requirements.txt
```

### Option 3: Use the Setup Script

Try running the setup script (if Python is available):

```powershell
python setup_environment.py
# OR
py setup_environment.py
```

## After Fixing Environment

Once dependencies are installed, you can run:

```powershell
# Activate virtual environment (if using one)
.\spacyenv\Scripts\activate

# Train the model
python scripts/train.py

# Run evaluation
python run_evaluation.py
```

## Verify Installation

Check if packages are installed:

```powershell
python -c "import numpy; import pandas; import sklearn; print('All packages installed!')"
```


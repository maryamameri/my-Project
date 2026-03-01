# README

## Project Overview
This project includes two Python scripts:

1. `import.py`: Handles data import and preprocessing.
2. `classification.py`: Implements a classification model.

## Prerequisites
Ensure you have the following dependencies installed before running the scripts:
```bash
pip install pandas numpy scikit-learn matplotlib
```

## File Descriptions

### `import.py`
- Loads datasets.
- Performs initial data preprocessing (e.g., handling missing values, encoding categorical variables).
- Exports processed data for further analysis.

### `classification.py`
- Loads preprocessed data from `import.py`.
- Splits data into training and testing sets.
- Trains a classification model using `scikit-learn`.
- Evaluates model performance using metrics like accuracy and confusion matrix.

## How to Run
1. Run `import.py` first to preprocess and save the dataset:
   ```bash
   python import.py
   ```
2. Then, execute `classification.py` to train and evaluate the model:
   ```bash
   python classification.py
   ```

## Output
- `import.py` generates a processed dataset file.
- `classification.py` prints model accuracy and displays performance metrics.

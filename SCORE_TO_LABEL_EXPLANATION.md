# How Similarity Scores are Matched to Labels

## Overview

The job-CV matching system uses **cosine similarity** to measure how well a resume matches a job description. The similarity score (ranging from 0.0 to 1.0) is then classified into one of three categories using **optimized thresholds**.

## The Matching Process

### Step 1: Compute Cosine Similarity

1. **Text Preprocessing**: Both the resume and job description are cleaned and normalized
2. **Vectorization**: Both texts are converted to TF-IDF vectors using a pre-trained vectorizer
3. **Similarity Calculation**: Cosine similarity is computed between the two vectors

**Cosine Similarity Formula:**
```
similarity = (A · B) / (||A|| × ||B||)
```

Where:
- `A · B` = dot product of vectors A and B
- `||A||` = L2 norm (magnitude) of vector A
- `||B||` = L2 norm (magnitude) of vector B

**Score Range:** 0.0 (completely different) to 1.0 (identical)

### Step 2: Classify Using Thresholds

The similarity score is compared against **two optimized thresholds** to determine the classification:

```
┌─────────────────────────────────────────────────────────────┐
│ If similarity_score >= good_fit_threshold        → 'Good Fit'      │
│ If potential_fit_threshold <= score < good_fit_threshold → 'Potential Fit' │
│ If similarity_score < potential_fit_threshold         → 'No Fit'        │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Threshold Values

The thresholds are stored in `saved_model/thresholds.json` after training. Default values:
- **Potential Fit Threshold**: ~0.40 (typically ranges from 0.20 to 0.60)
- **Good Fit Threshold**: ~0.70 (typically ranges from 0.50 to 0.90)

These thresholds are **optimized during training** using grid search to maximize the weighted F1-score on the validation set.

## Example Classifications

| Similarity Score | Classification | Explanation |
|-----------------|----------------|-------------|
| 0.85 | **Good Fit** | High similarity - strong match between CV and job |
| 0.75 | **Good Fit** | Above good threshold - indicates strong alignment |
| 0.65 | **Potential Fit** | Between thresholds - moderate match, worth considering |
| 0.50 | **Potential Fit** | Above potential threshold - some alignment present |
| 0.30 | **No Fit** | Below potential threshold - weak match |
| 0.10 | **No Fit** | Very low similarity - poor alignment |

## Code Implementation

The classification logic is implemented in `app/model.py`:

```python
def _classify_by_threshold(self, similarity_score: float) -> str:
    if similarity_score >= self.good_fit_threshold:
        return "Good Fit"
    elif similarity_score >= self.potential_fit_threshold:
        return "Potential Fit"
    else:
        return "No Fit"
```

## Threshold Optimization

During training (`scripts/train.py`), the system:

1. **Splits data** into train/validation/test sets (60/20/20)
2. **Computes similarity scores** for all validation examples
3. **Grid searches** over threshold combinations:
   - Potential threshold: 0.20 to 0.60 (step 0.01)
   - Good threshold: 0.50 to 0.90 (step 0.01)
4. **Selects thresholds** that maximize weighted F1-score on validation set
5. **Evaluates** on test set and saves thresholds to `saved_model/thresholds.json`

## How to Run

### 1. Train the Model

```bash
# Activate virtual environment (if using)
.\spacyenv\Scripts\activate  # Windows
source spacyenv/bin/activate  # Linux/Mac

# Run training script
python scripts/train.py
```

This will:
- Load data from `data/train.csv`
- Train TF-IDF vectorizer
- Optimize thresholds
- Save model to `saved_model/job_match_pipeline.joblib`
- Save thresholds to `saved_model/thresholds.json`

### 2. Run Evaluation

```bash
# Run evaluation script
python run_evaluation.py
```

This will:
- Load the trained model
- Evaluate on test data
- Show detailed metrics
- Explain score-to-label matching

## Understanding the Metrics

After evaluation, you'll see:

- **Accuracy**: Overall percentage of correct predictions
- **Precision**: Of items predicted as a class, how many were actually that class
- **Recall**: Of items that are actually a class, how many were correctly predicted
- **F1-Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Shows how predictions compare to true labels

## How the Model Learns Thresholds (e.g., 0.7 for "Good Fit")

**Important:** The model doesn't "know" that 0.7 is the threshold - it **learns** the optimal thresholds through an automated optimization process called **grid search** during training.

### The Learning Process:

1. **Grid Search**: The model tries thousands of threshold combinations:
   - Potential threshold: 0.20 to 0.60 (step 0.01) = 41 values
   - Good threshold: 0.50 to 0.90 (step 0.01) = 41 values
   - Total combinations tested: ~1,681

2. **Evaluation**: For each combination, the model:
   - Classifies all validation examples
   - Compares predictions to true labels
   - Calculates weighted F1-score (performance metric)

3. **Selection**: The model selects the threshold combination that gives the **highest F1-score**

4. **Result**: The optimal thresholds might be 0.42 and 0.73, or 0.38 and 0.68, etc. - **not necessarily 0.40 and 0.70!**

See `HOW_THRESHOLDS_ARE_LEARNED.md` for a detailed explanation.

## Summary

The score-to-label matching is a **threshold-based classification** system:
- **High scores (≥ good threshold)** → Strong match → "Good Fit"
- **Medium scores (≥ potential threshold, < good threshold)** → Moderate match → "Potential Fit"  
- **Low scores (< potential threshold)** → Weak match → "No Fit"

The thresholds are automatically optimized during training to maximize classification performance. The values (like 0.7) are **learned from your data**, not hardcoded!


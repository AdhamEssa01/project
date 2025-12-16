# How the Model Learns Thresholds (e.g., 0.7 for "Good Fit")

## The Key Question: How Does the Model Know 0.7 is for "Good Fit"?

**Short Answer:** The model doesn't "know" that 0.7 is the threshold - it **learns** the optimal thresholds through an automated optimization process called **grid search** during training.

## The Learning Process

### Step 1: Compute Similarity Scores

First, the model computes cosine similarity scores for all resume-job pairs in the validation set:

```python
# For each resume-job pair:
similarity_score = cosine_similarity(resume_vector, job_vector)
# Result: A number between 0.0 and 1.0
```

### Step 2: Grid Search Optimization

The model tries **thousands of threshold combinations** to find the best ones:

```python
# From scripts/train.py - find_optimal_thresholds()

potential_range = (0.20, 0.60)  # Try values from 0.20 to 0.60
good_range = (0.50, 0.90)      # Try values from 0.50 to 0.90
step = 0.01                    # Try every 0.01 increment

# This creates thousands of combinations:
# - potential_threshold: 0.20, 0.21, 0.22, ..., 0.60 (41 values)
# - good_threshold: 0.50, 0.51, 0.52, ..., 0.90 (41 values)
# - Total combinations: 41 × 41 = 1,681 (minus invalid ones)
```

### Step 3: Evaluate Each Combination

For each threshold combination, the model:

1. **Classifies** all validation examples using those thresholds
2. **Compares** predictions to true labels
3. **Calculates** the weighted F1-score (a performance metric)
4. **Keeps track** of the best-performing combination

```python
for potential_threshold in [0.20, 0.21, 0.22, ..., 0.60]:
    for good_threshold in [0.50, 0.51, 0.52, ..., 0.90]:
        if good_threshold <= potential_threshold:
            continue  # Skip invalid (good must be > potential)
        
        # Classify all examples with these thresholds
        predictions = classify_by_threshold(similarity_scores, 
                                           potential_threshold, 
                                           good_threshold)
        
        # Calculate how well these thresholds perform
        f1_score = calculate_f1_score(true_labels, predictions)
        
        # Remember the best combination
        if f1_score > best_f1_score:
            best_f1_score = f1_score
            best_potential = potential_threshold
            best_good = good_threshold
```

### Step 4: Select Optimal Thresholds

After trying all combinations, the model selects the thresholds that gave the **highest F1-score**:

```python
# Example result:
best_potential = 0.42  # Not necessarily 0.40!
best_good = 0.73       # Not necessarily 0.70!
best_f1_score = 0.85   # Best performance achieved
```

### Step 5: Save the Learned Thresholds

The optimal thresholds are saved to `saved_model/thresholds.json`:

```json
{
  "potential_fit_threshold": 0.42,
  "good_fit_threshold": 0.73,
  "optimization_metrics": {
    "validation_f1": 0.85
  }
}
```

## Why Not Hardcode 0.7?

The optimal threshold depends on:
- **Your specific data**: Different datasets have different score distributions
- **Label distribution**: If you have more "Good Fit" examples, thresholds might be different
- **Data quality**: Cleaner data might allow higher thresholds
- **Feature space**: The TF-IDF vocabulary affects similarity score ranges

## Example: Why 0.7 Might Not Be Optimal

Imagine two scenarios:

### Scenario A: High-Quality Matches
```
Similarity scores for "Good Fit" examples: [0.75, 0.82, 0.88, 0.91, ...]
Similarity scores for "Potential Fit":    [0.45, 0.52, 0.58, 0.61, ...]
Similarity scores for "No Fit":           [0.15, 0.22, 0.28, 0.31, ...]
```
**Optimal threshold might be: 0.75** (higher, because scores are generally higher)

### Scenario B: Lower-Quality Matches
```
Similarity scores for "Good Fit" examples: [0.65, 0.68, 0.72, 0.75, ...]
Similarity scores for "Potential Fit":    [0.35, 0.42, 0.48, 0.51, ...]
Similarity scores for "No Fit":           [0.10, 0.18, 0.25, 0.29, ...]
```
**Optimal threshold might be: 0.65** (lower, because scores are generally lower)

The grid search finds the threshold that best separates these distributions for **your specific data**.

## The Classification Logic (After Learning)

Once thresholds are learned, classification is simple:

```python
def classify(similarity_score, potential_threshold, good_threshold):
    if similarity_score >= good_threshold:      # e.g., >= 0.73
        return "Good Fit"
    elif similarity_score >= potential_threshold: # e.g., >= 0.42
        return "Potential Fit"
    else:
        return "No Fit"
```

## Visual Representation

```
Similarity Score Distribution:
│
│  No Fit        Potential Fit        Good Fit
│  ████          ████████            ████████
│  ████          ████████            ████████
│  ████          ████████            ████████
│  ████          ████████            ████████
│  ████          ████████            ████████
│────────────────┼────────────────────┼──────────────
0.0           0.42 (learned)       0.73 (learned)   1.0
              ↑                      ↑
         Potential Threshold    Good Threshold
```

The grid search finds the **best split points** (thresholds) that maximize classification accuracy.

## Summary

1. **0.7 is NOT hardcoded** - it's a default/starting point
2. **The model learns optimal thresholds** through grid search
3. **Grid search tries thousands of combinations** (0.20-0.60 for potential, 0.50-0.90 for good)
4. **Best combination is selected** based on F1-score on validation data
5. **Learned thresholds are saved** to `thresholds.json`
6. **During prediction**, the model uses these learned thresholds

The actual optimal threshold might be 0.65, 0.72, 0.78, or any value in the search range - it depends entirely on your training data!


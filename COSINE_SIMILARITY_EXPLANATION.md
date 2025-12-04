# Cosine Similarity-Based Job-CV Matching System

## Overview

This project uses a **cosine similarity-based approach** to determine how well a candidate's CV matches a job description. Unlike the previous supervised Logistic Regression classifier, this system computes similarity directly between vectorized texts and classifies matches using fixed thresholds.

## How the System Works

### 1. Training Phase (`scripts/train.py`)

**Purpose**: Fit a TF-IDF vectorizer on the training corpus to learn vocabulary and term weights.

**Process**:
1. Load training data from `data/train.csv`
2. Preprocess all resume texts and job description texts using `clean_text()`
3. **Create combined corpus**: Sum all resume texts and all job description texts into a single list
   - This ensures the vectorizer learns from the entire dataset
   - Provides consistent feature space for both CV and job description vectors
4. Fit TF-IDF vectorizer on the combined corpus with parameters:
   - `max_features=20000`: Top 20,000 features by term frequency
   - `ngram_range=(1, 2)`: Unigrams and bigrams
   - `stop_words="english"`: Removes English stopwords
5. Save the fitted vectorizer to `saved_model/job_match_pipeline.joblib`

**Key Code Location**: `scripts/train.py`, function `create_combined_corpus()`
- Lines 73-87: Corpus creation by concatenating resume and job description lists

### 2. Inference Phase (`app/model.py`)

**Purpose**: Compute cosine similarity between a CV and job description, then classify the match.

**Process**:

#### Step 1: Preprocessing
- Both CV and job description texts are preprocessed separately using `clean_text()`
- **Location**: `app/model.py`, lines 105-106

#### Step 2: Vectorization
- Both texts are vectorized **separately** using the loaded TF-IDF vectorizer
- This creates sparse vectors in the same feature space learned during training
- **Location**: `app/model.py`, lines 108-109

#### Step 3: Cosine Similarity Calculation
- Compute cosine similarity between the two vectors
- **Location**: `app/model.py`, lines 111-140

**Mathematical Formula**:
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

Where:
- `A · B` = dot product of vectors A and B (sum of element-wise products)
- `||A||` = L2 norm (magnitude) of vector A = √(sum of squares)
- `||B||` = L2 norm (magnitude) of vector B = √(sum of squares)

**For TF-IDF vectors** (which are non-negative), cosine similarity ranges from **0 to 1**:
- **0** = completely different (no shared terms)
- **1** = identical (same term weights)

**Implementation**: Uses `sklearn.metrics.pairwise.cosine_similarity()` which computes:
- Numerator: dot product (A · B)
- Denominator: ||A|| × ||B||
- Result: numerator / denominator

#### Step 4: Classification
- Apply fixed thresholds to convert similarity score into classification label
- **Location**: `app/model.py`, function `_classify_by_threshold()`, lines 67-84

**Thresholds**:
- `score >= 0.70` → **"Good Fit"**
- `0.40 <= score < 0.70` → **"Potential Fit"**
- `score < 0.40` → **"No Fit"**

### 3. API Response (`api/api.py`)

**Endpoint**: `POST /predict_fit`

**Response Format**:
```json
{
  "similarity_score": 0.75,
  "classification": "Good Fit"
}
```

**Key Code Location**: `api/api.py`, lines 60-68

## Differences from Previous Logistic Regression Approach

### Previous System (Logistic Regression)
1. **Training**: Trained a supervised classifier on labeled pairs
2. **Input**: Concatenated CV and job description with `[SEP]` separator
3. **Method**: TF-IDF vectorization → Logistic Regression → Class probabilities
4. **Decision**: Argmax of class probabilities (learned decision boundaries)
5. **Output**: `{predicted_fit, class_probabilities}`

### Current System (Cosine Similarity)
1. **Training**: Fits TF-IDF vectorizer on combined corpus (unsupervised)
2. **Input**: CV and job description kept separate
3. **Method**: Separate vectorization → Cosine similarity → Threshold-based classification
4. **Decision**: Fixed thresholds (0.40, 0.70) applied to similarity score
5. **Output**: `{similarity_score, classification}`

### Key Advantages
- **Interpretability**: Similarity score directly indicates match quality
- **No labeled data required**: Only needs corpus for vocabulary learning
- **Transparency**: Clear mathematical formula and explicit thresholds
- **Simplicity**: No complex model training, just vectorization and similarity

### Key Limitations
- **Fixed thresholds**: Not learned from data, may need tuning
- **No learning**: Doesn't learn which features are more important for matching
- **TF-IDF limitations**: May not capture semantic similarity as well as embeddings

## Code Locations

### Training
- **Main script**: `scripts/train.py`
- **Corpus creation**: `scripts/train.py`, function `create_combined_corpus()` (lines 73-87)
- **Vectorizer fitting**: `scripts/train.py`, function `main()` (lines 95-115)
- **Model saving**: `scripts/train.py`, function `save_vectorizer()` (lines 89-97)

### Inference
- **Model loading**: `app/model.py`, class `JobFitClassifier.load()` (lines 48-58)
- **Preprocessing**: `app/model.py`, `predict()` method (lines 105-106)
- **Vectorization**: `app/model.py`, `predict()` method (lines 108-109)
- **Cosine similarity**: `app/model.py`, `predict()` method (lines 111-140)
- **Classification**: `app/model.py`, function `_classify_by_threshold()` (lines 67-84)

### API
- **Endpoint**: `api/api.py`, function `predict_fit()` (lines 44-68)
- **Response construction**: `api/api.py`, lines 60-68

## TF-IDF Model Storage

**File**: `saved_model/job_match_pipeline.joblib`

**Contents**: Fitted `TfidfVectorizer` object containing:
- Vocabulary (word → feature index mapping)
- IDF (Inverse Document Frequency) weights for each feature
- Vectorizer configuration (max_features, ngram_range, stop_words, etc.)

**Loading**: Uses `joblib.load()` to deserialize the vectorizer object
- **Location**: `app/model.py`, line 55

**Usage**: The loaded vectorizer transforms new texts into vectors using the same vocabulary and IDF weights learned during training, ensuring consistent feature space for similarity computation.

## Threshold Application

The thresholds are applied in the `_classify_by_threshold()` method:

```python
if similarity_score >= 0.70:
    return "Good Fit"
elif similarity_score >= 0.40:
    return "Potential Fit"
else:
    return "No Fit"
```

**Why these thresholds?**
- **0.70**: High similarity indicates strong match (shared vocabulary and term weights)
- **0.40**: Moderate similarity indicates potential match (some overlap)
- **< 0.40**: Low similarity indicates poor match (minimal overlap)

These thresholds are fixed and not learned from data. They can be adjusted based on domain knowledge or evaluation metrics.

## Debugging Information

The code includes comments explaining:
- Vector shapes after transformation
- Cosine similarity formula and computation
- Which threshold is triggered (implicitly via classification result)

For additional debugging, you can add logging to print:
- TF-IDF vector shapes: `resume_vector.shape`, `job_vector.shape`
- Similarity score before thresholding
- Classification result

## Summary

This system replaces the supervised Logistic Regression classifier with a cosine similarity-based approach that:
1. Trains a TF-IDF vectorizer on a combined corpus
2. Vectorizes CV and job description separately during inference
3. Computes cosine similarity between vectors
4. Classifies using fixed thresholds (0.40, 0.70)

The system maintains the same project structure and API endpoints while providing a more interpretable and transparent matching mechanism.


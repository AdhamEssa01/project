from typing import Dict, List

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


CLASS_LABELS = ["No Fit", "Potential Fit", "Good Fit"]


def compute_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, labels: List[str] = None
) -> Dict:
    if labels is None:
        labels = CLASS_LABELS
    
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    
    per_class_metrics = {}
    for i, label in enumerate(labels):
        per_class_metrics[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1_score": float(f1[i]),
            "support": int(support[i]),
        }
    
    macro_precision = float(np.mean(precision))
    macro_recall = float(np.mean(recall))
    macro_f1 = float(np.mean(f1))
    
    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average="weighted", zero_division=0
        )
    )
    
    return {
        "accuracy": float(accuracy),
        "per_class": per_class_metrics,
        "macro_avg": {
            "precision": macro_precision,
            "recall": macro_recall,
            "f1_score": macro_f1,
        },
        "weighted_avg": {
            "precision": float(weighted_precision),
            "recall": float(weighted_recall),
            "f1_score": float(weighted_f1),
        },
    }


def generate_classification_report(
    y_true: np.ndarray, y_pred: np.ndarray, labels: List[str] = None
) -> Dict:
    if labels is None:
        labels = CLASS_LABELS
    
    return classification_report(
        y_true, y_pred, labels=labels, output_dict=True, zero_division=0
    )


def get_confusion_matrix(
    y_true: np.ndarray, y_pred: np.ndarray, labels: List[str] = None
) -> np.ndarray:
    if labels is None:
        labels = CLASS_LABELS
    
    return confusion_matrix(y_true, y_pred, labels=labels)

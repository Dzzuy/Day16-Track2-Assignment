"""Benchmark LightGBM on Kaggle's Credit Card Fraud Detection dataset."""

import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


def median_prediction_seconds(model, rows, repeats):
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        model.predict_proba(rows)
        timings.append(time.perf_counter() - start)
    return float(np.median(timings))


def main():
    seed = 16
    start = time.perf_counter()
    df = pd.read_csv("creditcard.csv")
    data_load_seconds = time.perf_counter() - start

    if "Class" not in df or len(df) < 1000 or df.isna().any().any():
        raise ValueError("Dataset is missing Class, too small, or contains missing values")
    features = df.drop(columns="Class")
    labels = df["Class"]
    if set(labels.unique()) != {0, 1}:
        raise ValueError("Class must contain both 0 and 1")

    trainval_x, test_x, trainval_y, test_y = train_test_split(
        features, labels, test_size=0.2, random_state=seed, stratify=labels
    )
    train_x, valid_x, train_y, valid_y = train_test_split(
        trainval_x, trainval_y, test_size=0.25, random_state=seed,
        stratify=trainval_y,
    )

    model = lgb.LGBMClassifier(
        n_estimators=300, learning_rate=0.05, random_state=seed,
        n_jobs=2, verbosity=-1,
    )
    start = time.perf_counter()
    model.fit(
        train_x, train_y, eval_set=[(valid_x, valid_y)], eval_metric="auc",
        callbacks=[lgb.early_stopping(20, verbose=False)],
    )
    training_seconds = time.perf_counter() - start

    probabilities = model.predict_proba(test_x)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    one_row = test_x.iloc[:1]
    batch = test_x.iloc[:1000]
    model.predict_proba(one_row)
    model.predict_proba(batch)
    single_seconds = median_prediction_seconds(model, one_row, 50)
    batch_seconds = median_prediction_seconds(model, batch, 10)

    result = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "architecture": platform.machine(),
        "versions": {
            "python": platform.python_version(),
            "lightgbm": lgb.__version__,
            "sklearn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "dataset_rows": int(len(df)),
        "fraud_rows": int(labels.sum()),
        "seed": seed,
        "split": {
            "train": len(train_x), "validation": len(valid_x), "test": len(test_x)
        },
        "n_jobs": 2,
        "decision_threshold": 0.5,
        "data_load_seconds": data_load_seconds,
        "training_seconds": training_seconds,
        "best_iteration": int(model.best_iteration_),
        "auc_roc": float(roc_auc_score(test_y, probabilities)),
        "accuracy": float(accuracy_score(test_y, predictions)),
        "f1": float(f1_score(test_y, predictions, zero_division=0)),
        "precision": float(precision_score(test_y, predictions, zero_division=0)),
        "recall": float(recall_score(test_y, predictions, zero_division=0)),
        "latency_1_row_ms": single_seconds * 1000,
        "latency_repeats": 50,
        "throughput_1000_rows_per_second": len(batch) / batch_seconds,
        "throughput_repeats": 10,
        "inference_timing": "median predict_proba call; excludes data loading and model training",
    }
    output = json.dumps(result, indent=2, allow_nan=False)
    Path("benchmark_result.json").write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

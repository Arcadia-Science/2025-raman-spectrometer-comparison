"""
# Multi-classifier evaluation framework

This module provides a unified framework for running and comparing multiple machine learning
classifiers on the same dataset. It facilitates side-by-side performance evaluation using
consistent metrics.

## Origins
This module is a refactoring and enhancement of the original work by
[Shankar Rao Pandala](https://github.com/shankarpandala), author of
[lazypredict](https://github.com/shankarpandala/lazypredict). While the core concepts and approach
were inspired by their work, this implementation addresses several issues in the
original codebase:
- Fixed stability issues present in the latest version of the original repository
- Improved code organization and readability
- Enhanced documentation and type hints

## Features
- Run multiple classifiers with a single unified interface
- Consistent preprocessing and cross-validation across all models
- Standardized performance metrics for fair comparison
- Flexible architecture for adding new classifiers

## Usage
See the example in `BatchClassifier`.
"""

import time
from pprint import pprint

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from tqdm import tqdm

FloatArray = NDArray[np.float64]

DEFAULT_CLASSIFIERS = [
    LogisticRegression,
    RandomForestClassifier,
    DummyClassifier,
]

TRANSFORMERS = {
    "numeric": Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler()),
        ]
    ),
    "categorical_low": Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoding", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    ),
    "categorical_high": Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoding", OrdinalEncoder()),
        ]
    ),
}


def get_cardinality_split(
    dataframe: pd.DataFrame,
    categorical_columns: list[str],
    cardinality_threshold: int = 11,
) -> tuple[list[str], list[str]]:
    """Splits categorical columns into 2 lists based on their cardinality (i.e # of unique values).

    Args:
        dataframe:
            Input DataFrame.
        categorical_columns:
            A list of the categorical columns within the input DataFrame.
        cardinality_threshold:
            Threshold for determining whether a column has low or high cardinality.

    Returns:
        low_cardinality_columns:
            List of columns with low cardinality (below threshold).
        high_cardinality_columns:
            List of columns with high cardinality (above threshold).
    """
    mask = dataframe[categorical_columns].nunique() > cardinality_threshold
    high_cardinality_columns = categorical_columns[mask]
    low_cardinality_columns = categorical_columns[~mask]
    return low_cardinality_columns, high_cardinality_columns


class BatchClassifier:
    """Class for facilitating the comparison of a variety of classification algorithms.

    Attributes:
        classifiers : list, optional (default="all")
            When function is provided, trains the chosen classifier(s).
        verbose : int, optional (default=0)
            For the liblinear and lbfgs solvers set verbose to any positive
            number for verbosity.
        prediction : bool, optional (default=False)
            When set to True, the predictions of all the models models are returned as dataframe.

    Examples:
        >>> from sklearn.datasets import load_breast_cancer
        >>> from sklearn.model_selection import train_test_split
        >>> data = load_breast_cancer()
        >>> X = data.data
        >>> y = data.target
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
        >>> batch_classifier = BatchClassifier(return_predictions=True)
        >>> scores, predictions = batch_classifier.fit(X_train, X_test, y_train, y_test)
        >>> scores
            | model                  | accuracy | balanced_accuracy | f1_score | run_time_s |
            |------------------------|----------|-------------------|----------|------------|
            | LogisticRegression     | 0.985965 |          0.982690 | 0.985934 |  0.008263  |
            | RandomForestClassifier | 0.971930 |          0.971701 | 0.971987 |  0.068998  |
            | DummyClassifier        | 0.638596 |          0.500000 | 0.497750 |  0.003231  |
        >>> predictions
                | LogisticRegression | RandomForestClassifier | DummyClassifier |
            ----|--------------------|------------------------|-----------------|
            0   |                  1 |                      1 |               1 |
            1   |                  1 |                      1 |               1 |
            2   |                  0 |                      0 |               1 |
            ... |                ... |                    ... |             ... |
            282 |                  1 |                      1 |               1 |
            283 |                  1 |                      0 |               1 |
            284 |                  0 |                      0 |               1 |
    """

    def __init__(
        self,
        classifiers: None | list = None,
        return_predictions: bool = False,
        verbose: bool = False,
        random_state: int = 42,
    ):
        self.classifiers = classifiers
        self.return_predictions = return_predictions
        self.verbose = verbose
        self.random_state = random_state

        # Fall back to default classifiers if none are provided
        if self.classifiers is None:
            self.classifiers = DEFAULT_CLASSIFIERS

        self.models = {}

    def fit(
        self,
        X_train: FloatArray,
        X_test: FloatArray,
        y_train: FloatArray,
        y_test: FloatArray,
    ) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
        """Fit, predict, and evaluate classification algorithms.

        Each classification algorithm is fit to `X_train` and `y_train`; predictions are generated
        on `X_test` and evaluated on `y_test`. The training and testing data should be arranged
        such that each row is a sample and each column is a feature.

        Returns:
            scores:
                Performance metrics of each classifier as a pandas DataFrame.
            predictions:
                Predictions from each classifier as a pandas DataFrame.
        """
        # Convert training and testing data from numpy arrays to pandas DataFrames to
        # more easily determine the data type of each feature
        X_train = pd.DataFrame(X_train)
        X_test = pd.DataFrame(X_test)
        # Determine the type of data of each feature
        numeric_features = X_train.select_dtypes(include=[np.number]).columns
        categorical_features = X_train.select_dtypes(include=["object"]).columns
        low_cardinality_columns, high_cardinality_columns = get_cardinality_split(
            X_train, categorical_features
        )

        # Define feature transformers
        # https://scikit-learn.org/stable/modules/compose.html#column-transformer
        preprocessor = ColumnTransformer(
            transformers=[
                ("numeric", TRANSFORMERS["numeric"], numeric_features),
                ("categorical_low", TRANSFORMERS["categorical_low"], low_cardinality_columns),
                ("categorical_high", TRANSFORMERS["categorical_high"], high_cardinality_columns),
            ]
        )

        # Performance metrics to record
        results = {
            "model": [],
            "accuracy": [],
            "balanced_accuracy": [],
            "f1_score": [],
            "run_time_s": [],
        }
        predictions = {}

        # Run through each classifier
        disable = not self.verbose
        for model in tqdm(self.classifiers, disable=disable):
            model_name = model.__name__
            start_time = time.time()

            # Set random state when possible
            if "random_state" in model().get_params().keys():
                pipeline = Pipeline(
                    steps=[
                        ("preprocessor", preprocessor),
                        ("classifier", model(random_state=self.random_state)),
                    ]
                )
            else:
                pipeline = Pipeline(
                    steps=[
                        ("preprocessor", preprocessor),
                        ("classifier", model()),
                    ]
                )

            # Train/test on each classifier
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            # Evaluate
            accuracy = accuracy_score(y_test, y_pred, normalize=True)
            balanced_accuracy = balanced_accuracy_score(y_test, y_pred)
            f1_result = f1_score(y_test, y_pred, average="weighted")
            run_time_s = time.time() - start_time

            # Record metrics
            results["model"].append(model_name)
            results["accuracy"].append(accuracy)
            results["balanced_accuracy"].append(balanced_accuracy)
            results["f1_score"].append(f1_result)
            results["run_time_s"].append(run_time_s)
            # Record predictions
            predictions[model_name] = y_pred

            if self.verbose:
                out = {
                    metric: f"{values[-1]:.3g}"
                    for metric, values in results.items()
                    if metric != "model"
                }
                print(f"Model: {model_name}")
                pprint(out)

        # Convert results to a DataFrame and sort by balanced accuracy
        scores = pd.DataFrame.from_dict(results)
        scores = scores.sort_values(
            by="balanced_accuracy",
            ascending=False,
        ).set_index("model")
        # Convert predictions to a DataFrame
        predictions = pd.DataFrame.from_dict(predictions)

        if self.return_predictions:
            return scores, predictions
        else:
            return scores

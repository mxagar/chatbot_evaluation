"""This module handles the persistence of evaluation results,
saving them to a CSV file in the specified results directory.

Example usage:

    config = load_config(config_path="path/to/your/config.yaml")
    dataset = load_dataset(dataset_path="path/to/your/dataset.csv")
    results = run_evaluation(config,
                             dataset=dataset)
    params = {"param_1": "value_1", "param_2": "value_2"}
    log_evaluation_results(results, config, params)

Author: Mikel Sagardia
Date: 2024-02-28
"""
import os
import pandas as pd
from typing import List, Dict, Any, Optional
from .core import logger

def log_evaluation_results(results: List[Dict[str, Any]],
                           config: Dict[str, Any],
                           params: Optional[Dict[str, Any]] = None,
                           output_directory: str = './results',
                           output_filename: str = 'evaluation_results.csv') -> None:
    """Save evaluation results, along with config and params,
    to a CSV file."""
    results_df = pd.DataFrame(results)

    # Unpack score dictionaries into separate columns
    scores_df = results_df.pop('scores').apply(pd.Series)
    results_df = pd.concat([results_df, scores_df], axis=1)

    # Add config and params to the DataFrame as new columns with constant values
    scorers = config.get("scorers", [])
    if params is None:
        params = {}
    for key, value in {**config, **params}.items():
        if key in scorers:
            key = key + "_params"
        results_df[key] = [value] * len(results_df)

    # Specify the results directory and filename
    results_directory = config.get('results_directory', output_directory)
    os.makedirs(results_directory, exist_ok=True)
    filename = config.get('results_filename', output_filename)
    filepath = os.path.join(results_directory, filename)

    # Save DataFrame to CSV
    results_df.to_csv(filepath, index=False)
    logger.info(f"Saved evaluation results to: {filepath}")

"""This module contains the fixtures and
definitions used by pytest.

Author: Mikel Sagardia
Date: 2024-02-28
"""
import sys
import yaml
import pytest
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from chatbot_evaluation.evaluation import (
    load_config,
    load_dataset,
    load_chatbot,
    load_scorers
)


@pytest.fixture(scope="session")
def config():
    config_path = "tests/config_test.yaml"
    config_file = Path(config_path)

    if not config_file.is_file():
        pytest.fail(f"Configuration file does not exist: {config_path}")

    try:
        return load_config(config_path)
    except Exception as e:
        pytest.fail(f"Failed to load configuration: {e}")


@pytest.fixture(scope="session")
def dataset(config):
    dataset_path = config.get("dataset_path", "default/path/to/dataset.csv")
    dataset_file = Path(dataset_path)

    if not dataset_file.is_file():
        pytest.fail(f"Dataset file does not exist: {dataset_path}")

    try:
        return load_dataset(config)
    except Exception as e:
        pytest.fail(f"Failed to load dataset: {e}")


@pytest.fixture(scope="session")
def chatbot(config, dataset):
    return load_chatbot(config, dataset)


@pytest.fixture(scope="session")
def scorers(config):
    return load_scorers(config)

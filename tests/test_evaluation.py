"""This module contains the tests
of the chatbot_evaluation.evaluation module.

Usage:

    # Configure properly tests/config_test.yaml
    # and cd to the directory where you see tests/
    cd ...
    pytest tests

Author: Mikel Sagardia
Date: 2024-02-28
"""
import os
import pytest
import pandas as pd
from chatbot_evaluation.evaluation import run_evaluation
from chatbot_evaluation.core import (
    QAPair,
    ChatSession,
    ChatHistory
)
from chatbot_evaluation.dataset import (
    question_to_history,
    history_to_question
)
from chatbot_evaluation.persistence import log_evaluation_results


def test_config(config):
    assert isinstance(config, dict)
    assert "chatbot_type" in config
    assert config["chatbot_type"] in ["dummy", "api", "lib"]
    assert "dataset_path" in config


def test_dataset(dataset):
    assert dataset.dataset_type in ["single", "multiple"]
    assert dataset.data.shape[0] > 0
    assert dataset.data.shape[1] > 0

    for index, item in dataset:
        assert isinstance(item, QAPair) or isinstance(item, ChatSession)
        if index > 5:
            break


def test_chatbot(config, chatbot):
    assert chatbot.type == config["chatbot_type"]
    params = chatbot.get_parameters()
    assert isinstance(params, dict)
    
    if chatbot.type == "dummy":
        assert len(chatbot.answers) > 0
        answer = chatbot.get_response("What time is it?")
        assert (answer in chatbot.answers) or (answer == chatbot.default_answer)
    
    elif chatbot.type == "api":
        # TODO
        pass
    
    elif chatbot.type == "lib":
        # TODO
        pass


def test_scorers(config, scorers):
    assert isinstance(scorers, list)
    assert len(scorers) > 0
    for scorer in scorers:
        assert scorer.type[0] in config["scorers"]
        if scorer.type[0] == "dummy":
            reference = "This is a good answer."
            predicted = "This is a better answer."
            s = scorer.score(predicted=predicted, reference=reference)
            assert isinstance(s, float)
            assert s >= 0.0
            assert s <= 1.0

        elif scorer.type[0] == "bert":
            # TODO
            pass

        elif scorer.type[0] == "sbert":
            # TODO
            pass

        elif scorer.type[0] == "llm":
            # TODO
            pass


def test_run_evaluation(config, chatbot, scorers, dataset):
    results = run_evaluation(config=config, chatbot=chatbot, scorers=scorers, dataset=dataset)
    assert isinstance(results, list)
    assert len(results) > 0

    for result in results:
        assert "index" in result
        assert "question" in result
        assert "reference_answer" in result
        assert "predicted_answer" in result
        assert "duration" in result
        assert "scores" in result
        
        assert result["index"] > -1
        assert len(result["question"]) > 0
        assert len(result["reference_answer"]) > 0
        assert len(result["predicted_answer"]) > 0
        assert result["duration"] > -1.0

        for metric, score in result["scores"].items():
            assert metric.split("_")[0] in ["dummy", "bert", "sbert", "llm"]
            assert score >= 0.0
            assert score <= 1.0


def test_log_evaluation_results(config, chatbot, scorers, dataset):
    # FIXME: This test function should one to its own module test_persistence.py
    # FIXME: We should not run the evaluation again, but instead pass the results from previous test!
    # Run evaluation to get results
    results = run_evaluation(config=config, chatbot=chatbot, scorers=scorers, dataset=dataset)
    
    # Log
    params = {"param_1": "value_1", "param_2": "value_2"}
    output_directory = "./results"
    output_filename = "test_evaluation_results.csv"
    log_evaluation_results(results=results,
                           config=config,
                           params=params,
                           output_directory=output_directory,
                           output_filename=output_filename)

    # Open logged CSV
    filepath = os.path.join(output_directory, output_filename)
    df = pd.read_csv(filepath)
    
    # Checks
    print(df)
    assert df.shape[0] == dataset.data.shape[0]
    # ...


@pytest.mark.parametrize(
    'question',
    [
        "question 1",
        "question 2"
    ]
)
def test_question_to_history(question):
    # FIXME: This test function should one to its own module test_dataset.py
    history = question_to_history(question)
    assert isinstance(history, list)
    assert "user" in history[0]
    assert history[0]["user"] == question


@pytest.mark.parametrize(
    'history',
    [
        [{'user': 'question'}],
        [
            {'user': 'question one',
                'bot': 'answer one'},
            {'user': 'question two',
                'bot': 'answer two'},
            {'user': 'question three'} 
        ]
    ]
)
def test_history_to_question(history):
    # FIXME: This test function should one to its own module test_dataset.py
    # WARNING: Even though we parametrize history as a List[dict], it should be a List[ChatHistory]
    chat_history = [ChatHistory(**h) for h in history]
    question = history_to_question(chat_history)
    assert isinstance(question, str)
    if len(history) == 1:
        assert chat_history[0].user == question
    else:
        assert chat_history[-1].user in question

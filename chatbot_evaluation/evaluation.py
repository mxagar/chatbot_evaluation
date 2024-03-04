"""This module runs the evaluations.
It will load the dataset, instantiate a selected ChatBot object,
and loop over question-answer pairs from the specified dataset
to collect evaluation metrics, which are then sent to persistence.py.

This is the main entrypoint of the package/library.

Example usage:

    config = load_config(config_path="path/to/your/config.yaml")
    dataset = load_dataset(dataset_path="path/to/your/dataset.csv")
    results = run_evaluation(config,
                             dataset=dataset)

Then, the results List[dict] can be persisted using
persistence.log_evaluation_results().

Author: Mikel Sagardia
Date: 2024-02-28
"""
import yaml
import time
from typing import List, Optional
from .chatbot import (
    AbstractChatBot,
    ChatBotDummy,
    ChatBotAPI
)
from .dataset import (
    Dataset,
    extract_question_answer_ref,
    extract_answer_refs
)
from .scoring import (
    AbstractScorer,
    ScorerDummy,
    ScorerBERT,
    ScorerSBERT,
    SBERT_MODEL_NAME
)
from .core import (
    CONFIG_FILEPATH,
    DATASET_FILEPATH,
    get_token,
    get_api_url,
    logger
)


def load_config(filepath: str = CONFIG_FILEPATH) -> dict:
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)


def load_dataset(config: dict) -> Dataset:
    dataset_path = config.get("dataset_path", DATASET_FILEPATH)
    return Dataset(filepath=dataset_path)


def load_chatbot(config: dict,
                 dataset: Optional[Dataset] = None,
                 chatbot_type: Optional[str] = None) -> AbstractChatBot:
    if chatbot_type is None:
        chatbot_type = config.get("chatbot_type", "dummy")

    if chatbot_type == "dummy":
        answers = ["42.", "Great question.", "I don't know.", "Hakuna matata."]
        default_answer = answers[0]
        if dataset is not None:
            answers = extract_answer_refs(dataset)
        return ChatBotDummy(answers=answers, default_answer=default_answer)

    elif chatbot_type == "api":
        #url = get_api_url()
        url = config["api"].get("url", "https://localhost:8080")
        token_type = config["api"].get("token_type", "Bearer")
        token = get_token()
        return ChatBotAPI(url=url, token=token, token_type=token_type)

    elif chatbot_type == "lib":
        # Still to be implemented...
        raise NotImplementedError("ChatBotLib is not implemented yet.")

    else:
        raise ValueError(f"Unsupported chatbot type: {chatbot_type}")


def load_scorers(config: dict) -> List[AbstractScorer]:
    scorers = []
    for scorer_name in config.get("scorers", []):
        if scorer_name == "dummy":
            scorers.append(ScorerDummy(seed=42))
        if scorer_name == "bert":
            lang = "en"
            if config.get("bert", None) is not None:
                lang = config["bert"].get("lang", lang)
            scorers.append(ScorerBERT(lang=lang))
        elif scorer_name == "sbert":
            model_name = SBERT_MODEL_NAME
            if config.get("sbert", None) is not None:
                model_name = config["sbert"].get("model_name", model_name)
            scorers.append(ScorerSBERT(model_name=model_name))
    return scorers


def run_evaluation(config_path: str = CONFIG_FILEPATH,
                   config: Optional[dict] = None,
                   chatbot: Optional[AbstractChatBot] = None,
                   scorers: Optional[List[AbstractScorer]] = None,
                   dataset: Optional[Dataset] = None) -> List[dict]:
    """Run the evaluation process:
    - Load all necessary objects, if not passed: config, chatbot, scorers, dataset.
    - Run the scorers on the dataset.
    """
    # Load all necessary objects, is not passed
    if config is None:
        config = load_config(config_path)
        logger.info(f"Config file loaded: {config_path}")
    if chatbot is None:
        chatbot = load_chatbot(config)
        logger.info(f"Chatbot loaded: {config.get('chatbot_type', 'dummy')}")
    if scorers is None:
        scorers = load_scorers(config)
        logger.info(f"Scorers loaded: {config.get('scorers', ['dummy'])}")
    if dataset is None:
        dataset = load_dataset(config)
        logger.info(f"Dataset loaded: {config.get('dataset_path', './data/qa_pairs_dummy.csv')}")

    results = []
    for index, item in dataset:
        # Unpack question
        question, answer_ref = extract_question_answer_ref(item)

        # Chatbot generates an answer to the question
        start_time = time.time()
        answer_pred = chatbot.get_response(question)
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        logger.info(f"Q-A extracted: index {index}, question: {question[:(10 if len(question) > 10 else -1)]}")

        # Evaluate the answer using metrics (e.g., BERTScore, response time, etc.)
        score_dict = {}
        for scorer in scorers:
            scorer_metric = scorer.type[0] + "_" + scorer.type[1] # scorer_type_metric, e.g., dummy_similarity, bert_f1, sbert_cosine_sim
            score_dict[scorer_metric] = scorer.score(answer_pred, answer_ref)
        logger.info(f"Q-A scored: {score_dict}")

        # Pack the results
        result = {
            "index": index,
            "question": question,
            "reference_answer": answer_ref,
            "predicted_answer": answer_pred,
            "duration": duration,
            "scores": score_dict
        }

        results.append(result)

    return results        

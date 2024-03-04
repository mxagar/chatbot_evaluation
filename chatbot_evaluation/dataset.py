"""This module loads a Question-Answer dataset,
pre-processes it (if necessary)
and provides it as an iterable object.

Author: Mikel Sagardia
Date: 2024-02-28
"""
import ast
import pandas as pd
from typing import Iterator, Tuple, List, Union, Dict
from pydantic import ValidationError

from .core import (
    QAPair,
    ChatHistory,
    ChatSession,
    logger
)


class Dataset:
    """This class loads a dataset to be used to evaluate a chatbot.
    Two types of dataset formats are implemented at the moment.
    An iterable is returned, which consists of a tuple/pair (index, item).
    The dataset items are defined in core.py."""
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._dataset_type = None
        self._single_cols = list(QAPair.model_fields.keys()) # pair_id', 'question_id', 'answer_id', 'question_text', 'answer_text', 'answer_quality'
        self._multiple_cols = list(ChatSession.model_fields.keys()) # 'id', 'timestamp', 'history', 'rating', 'message'
        try:
            self._data = pd.read_csv(self._filepath)
            self._identify_dataset_type()
            self._preprocess_dataset()
        except FileNotFoundError as e:
            logger.error(f"File not found: {self._filepath}")
            raise e
        except Exception as e:
            logger.error(f"Error loading dataset from {self._filepath}: {e}")
            raise e

    def _identify_dataset_type(self) -> None:
        if set(self._single_cols).issubset(self._data.columns):
            self._dataset_type = "single"
        elif set(self._multiple_cols).issubset(self._data.columns):
            self._dataset_type = "multiple"
        else:
            raise ValueError("Unknown dataset format")

    def _preprocess_dataset(self) -> None:
        def _scale_rating(rating: int) -> float:
            """Scale rating from [1, 5] to [-1.0, 1.0]."""
            return ((float(rating) - 1.0) / (5.0 - 1.0)) * 2.0 - 1.0

        if self._dataset_type == "multiple":
            self._data['history'] = self._data['history'].apply(ast.literal_eval)
            self._data['message'] = self._data['message'].fillna("No message provided.")
            self._data['timestamp'] = pd.to_datetime(self._data['timestamp'], format='%d.%m.%Y, %H:%M:%S.%f')
            self._data['rating'] = self._data['rating'].apply(_scale_rating)
        elif self._dataset_type == "single":
            self._data['answer_text'] = self._data['answer_text'].fillna("")

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @property
    def dataset_type(self) -> str:
        return self._dataset_type

    def __iter__(self) -> Iterator[Union[QAPair, ChatSession]]:
        if self._dataset_type == "single":
            for idx, row in self._data.iterrows():
                try:
                    qa_pair = QAPair(
                        pair_id=row['pair_id'],
                        question_id=row['question_id'],
                        answer_id=row['answer_id'],
                        question_text=row['question_text'],
                        answer_text=row['answer_text'],
                        answer_quality=row['answer_quality']
                    )
                    yield idx, qa_pair
                except ValidationError as e:
                    logger.error(f"Error validating row {idx}: {e}")
                    raise e

        elif self._dataset_type == "multiple":
            for idx, row in self._data.iterrows():
                try:
                    history_items = [ChatHistory(**item) for item in row['history']]
                    chat_session = ChatSession(
                        id=row['id'],
                        timestamp=row['timestamp'],
                        history=history_items,
                        rating=row['rating'],
                        message=row['message']
                    )
                    yield idx, chat_session
                except ValidationError as e:
                    logger.error(f"Error validating row {idx}: {e}")
                    raise e


def question_to_history(question: str) -> List[Dict[str, str]]:
    """Formats a single question string into a chat history."""
    return [{'user': question}]


def history_to_question(history: List[ChatHistory],
                        #history: List[Dict[str, str]],
                        language: str = "en") -> str:
    """Formats the chat history into a single question string.
    
    Possible history objects:
    
        history = [{'user': 'question'}]

        history = [
            {'user': 'question one',
             'bot': 'answer one'},
            {'user': 'question two',
             'bot': 'answer two'},
            {'user': 'question three'} 
        ]
    """
    question = ""
    
    if history is not None:        
        if len(history) == 1:
            question = history[-1].user

        else:
            prompt_presentation = "This is our past conversation:"
            prompt_query = "Now, this is my last question, which you are asked to answer:"
            if language == "de":
                prompt_presentation = "Dies ist unser bisheriges Gespräch:"
                prompt_query = "Nun, hier ist meine letzte Frage, die du beantworten sollst:"

            conversation = '\n'.join([f'User: {entry.user}\nBot: {entry.bot if entry.bot else "No response."}' for entry in history[:-1]])
            question = f"{prompt_presentation}\n\n{conversation}\n\n{prompt_query}\n\nUser: {history[-1].user}"

    return question


def extract_question_answer_ref(item: Union[QAPair, ChatSession]) -> Tuple[str, str]:
    """This function takes a Dataset item
    and returns a pair (question: str, answer: str)."""
    question = None
    answer_ref = None
    if isinstance(item, QAPair):  # QAPair, dataset.dataset_type == "single"
        question = item.question_text
        answer_ref = item.answer_text
    elif isinstance(item, ChatSession):  # ChatSession, dataset.dataset_type == "multiple"
        question = history_to_question(item.history)
        last_chat_history_item = item.history[-1]
        answer_ref = last_chat_history_item.bot if last_chat_history_item.bot else "No reference answer provided."
        
    return question, answer_ref


def extract_answer_refs(dataset: Dataset) -> List[str]:
    """This function takes a Dataset and fetches
    all the answers contained in it."""
    answers = []
    if dataset.dataset_type == "single": # QAPair
        answers = dataset.data['answer_text'].to_list()
    elif dataset.dataset_type == "multiple":  # ChatSession
        for _, item in dataset:
            last_chat_history_item = item.history[-1]
            answer_ref = last_chat_history_item.bot if last_chat_history_item.bot else "No reference answer provided."
            answers.append(answer_ref)

    return answers

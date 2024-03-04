"""This module contains the different implementations
of the ChatBot classes,
derived from the abstract class AbstractChatBot:

- ChatBotDummy: randomly selects an answer from a predefined list.
- ChatBotAPI: sends questions to a remote API.
- ChatBotLib: connects to a local LLM using a library.

Author: Mikel Sagardia
Date: 2024-02-28
"""
import random
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
from .core import (
    logger
)
from .core import (
    ChatHistory
)
from .dataset import (
    question_to_history,
    history_to_question
)


class AbstractChatBot(ABC):
    @abstractmethod
    def get_response(self, history: Union[str, List[Dict[str, str]]]) -> str:
        """Return a response to the given question, possibly embedded in a history."""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict:
        """Automatically get the configuration parameters."""
        pass


class ChatBotDummy(AbstractChatBot):
    """This chatbot randomly selects and answer
    from a predefined list."""
    def __init__(self,
                 answers: Optional[List[str]] = None,
                 default_answer: Optional[str] = None):
        if not answers and not default_answer:
            logger.error("Must provide at least one answer or a default answer.")
            raise ValueError("Must provide at least one answer or a default answer.")
        self._answers = answers or []  # Initialize with an empty list if None
        self._default_answer = default_answer
        self._chatbot_type = "dummy"

    @property
    def type(self) -> str:
        return self._chatbot_type

    @property
    def default_answer(self) -> Optional[str]:
        return self._default_answer

    @default_answer.setter
    def default_answer(self, new_default_answer: Optional[str]) -> None:
        if not new_default_answer:
            logger.error("Default answer cannot be empty.")
            raise ValueError("Default answer cannot be empty.")
        self._default_answer = new_default_answer

    @property
    def answers(self) -> List[str]:
        return self._answers

    @answers.setter
    def answers(self, new_answers: List[str]) -> None:
        if not new_answers:
            logger.error("Answers list cannot be empty.")
            raise ValueError("Answers list cannot be empty.")
        self._answers = new_answers

    def get_parameters(self) -> Dict:
        return {
            "chatbot_type": self._chatbot_type
        }

    #def get_response(self, history: Union[str, List[Dict[str, str]]]) -> str:
    def get_response(self, history: Union[str, List[ChatHistory]]) -> str:
        if isinstance(history, list):
            question = history_to_question(history)
        else:
            question = history
        logger.info(f"Received question...")

        if self._answers:
            answer = random.choice(self._answers)
            logger.info(f"Returning random answer: {answer[:(10 if len(answer) > 10 else -1)]}...")
            return answer
        elif self._default_answer:
            return self._default_answer
        else:
            dont_know = "I'm not sure how to respond to that."
            logger.warning(f"No answers available, returning '{dont_know}'.")
            return dont_know


class ChatBotAPI(AbstractChatBot):
    """ChatBot which requests posts to a REST API endpoint.
    The REST API endpoint handling needs to be modified for
    each case.
    """
    def __init__(self,
                 url: str,
                 token: str,
                 token_type: str = "Bearer",
                 approach: str = "abc",
                 retrieval_mode: str = "hybrid"):
        self._url = f"https://{url}/chat"  # Modify if required
        self._token = token # TODO: This is not secure! Consider encryption...
        self._token_type = token_type
        self._approach = approach
        self._retrieval_mode = retrieval_mode
        self._headers = {"Authorization": f"{self._token_type} {self._token}"}
        self._chatbot_type = "api"

    @property
    def type(self) -> str:
        return self._chatbot_type

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, new_url: str) -> None:
        self._url = new_url

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, new_token: str) -> None:
        self._token = new_token
        self._headers["Authorization"] = f"{self._token_type} {self._token}"

    def get_parameters(self) -> Dict:
        # TODO: Automatically get the configuration parameters from API?
        return {
            "chatbot_type": self._chatbot_type,
            "url": self._url,
            "approach": self._approach,
            "retrieval_mode": self._retrieval_mode,
            # Model version, etc.?
        }

    def get_response(self, history: Union[str, List[Dict[str, str]]]) -> str:
        """Feed history (which includes question) and get an answer
        for it.
        
        Possible history objects:
        
            history = [{'user': 'question'}]

            history = [
                {'user': 'question one',
                 'bot': 'answer one'},
                {'user': 'question two',
                 'bot': 'answer two'},
                {'user': 'question two'} 
            ]
        """
        if isinstance(history, str):
            history = question_to_history(history)
        payload = {
            "history": history,
            "approach": self._approach,
            "overrides": {
                "retrieval_mode": self._retrieval_mode,
                "semantic_ranker": True,
                "semantic_captions": False,
                "top": 3,
                "temperature": 0.7,
                "category_filter": []
            }
        }

        try:
            logger.info(f"Posting received question...")
            response = requests.post(self.url, headers=self._headers, json=payload, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            answer = response.json().get('answer', "Sorry, I couldn't process your question.")
            logger.info(f"Post response received: {answer[:(10 if len(answer) > 10 else -1)]}...")
            return answer
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout error occurred: {timeout_err}")
        except Exception as err:
            logger.error(f"Other error occurred: {err}")

        return "I'm having trouble connecting to the server right now."


class ChatBotLib(AbstractChatBot):
    """This chatbot connects to a local LLM via a library.
    It needs to be implemented."""
    def __init__(self, model_path: str):
        self._model_path = model_path
        self._chatbot_type = "lib"
        # TODO: Load the model using the library
        # ...

    def get_response(self, question: str) -> str:
        # TODO: Implement the logic to get a response from the loaded model
        # ...
        pass

    def get_parameters(self) -> Dict:
        # TODO: Automatically get the configuration parameters?
        # ...
        pass

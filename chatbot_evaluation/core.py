"""This module contains common constants,
utility functions, and base classes
used in the package.

Author: Mikel Sagardia
Date: 2024-02-28
"""
import os
from dotenv import load_dotenv
import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging

# Constants
DEFAULT_RESPONSE_TIME_LIMIT = 5  # seconds
LOG_FILENAME = "chatbot_evaluation.log"
CONFIG_FILEPATH = "./config_eval.yaml"
DATASET_FILEPATH = "./data/qa_pairs_dummy.csv"
#DATASET_FILEPATH = "./data/chat_history_dummy.csv"

# Configure logging
logging.basicConfig(level=logging.INFO, # WARNING
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILENAME,
                    filemode='a')  # 'w' to overwrite

# Create a logger object for the package
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv() # CHATBOT_API_TOKEN


class QAPair(BaseModel):
    pair_id: int
    question_id: int
    answer_id: int
    question_text: str
    answer_text: str
    answer_quality: float


class ChatHistory(BaseModel):
    user: str
    bot: Optional[str] = None


class ChatSession(BaseModel):
    id: int
    timestamp: datetime.datetime
    history: List[ChatHistory]
    rating: float
    message: str


def get_token() -> str:
    return os.getenv("CHATBOT_API_TOKEN")


def get_api_url() -> str:
    return os.getenv("CHATBOT_API_URL")

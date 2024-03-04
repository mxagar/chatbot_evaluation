"""This module checks a chat history dataset.
This module will be deleted,
it's purpose is for temporary testing.

Usage:

    python ./check_data.py

Author: Mikel Sagardia
Date: 2024-02-28
"""
import ast
import datetime
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any
import pandas as pd

DATASET_PATH = "./chat_history_dummy.csv"

class Sample:
    def __init__(self):
        self.id = 5
        self.timestamp = "4.1.2024, 12:20:40.000"
        self.rating = 2
        self.history = [
            {'user': 'What day is today?',
             'bot': 'Today is the second day of the week.'},
            {'user': 'And which day is that?',
             'bot': 'Tuesday.'}
        ]
        self.message = "It doesn't go to the point."


class ChatHistory(BaseModel):
    user: str
    bot: str


class ChatSession(BaseModel):
    id: int
    timestamp: datetime.datetime
    history: List[ChatHistory]
    rating: float
    message: str


def _convert_history(row: str) -> List[Dict[str, Any]]:
    try:
        return ast.literal_eval(row)
    except ValueError as e:
        print(f"Error converting history: {e}")
        return []


def _scale_rating(rating: int) -> float:
    """Scale rating from [1, 5] to [-1.0, 1.0]."""
    return ((float(rating) - 1.0) / (5.0 - 1.0)) * 2.0 - 1.0


def check_sample(sample: Sample) -> bool:
    # Convert Sample instance to ChatHistory instances and then to a ChatSession instance
    try:
        history_items = [ChatHistory(**item) for item in sample.history]
        _ = ChatSession(
            id=sample.id,
            timestamp=pd.to_datetime(sample.timestamp, format='%d.%m.%Y, %H:%M:%S.%f'),
            history=history_items,
            rating=_scale_rating(sample.rating),
            message=sample.message
        )
    except ValidationError as e:
        print(f"Error creating ChatHistory from Sample: {e}")
        raise e

    return True


def check_dataset(dataset_path: str = DATASET_PATH) -> bool:
    # Load the CSV
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError as e:
        print(f"Missing file {dataset_path}: {e}")
        raise e

    # Convert 'timestamp' column to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d.%m.%Y, %H:%M:%S.%f')

    # Convert the 'history' column from string to actual lists of dictionaries
    df['history'] = df['history'].apply(_convert_history)

    # Replace NaN values in the 'message' column with a default string
    df['message'] = df['message'].fillna("No message provided.")

    # Use the Pydantic model to parse and validate the data
    for index, row in df.iterrows():
        try:
            # Validate each item in the history list as ChatHistory, then ChatSession
            history_items = [ChatHistory(**item) for item in row['history']]
            chat_session = ChatSession(
                id=row['id'],
                timestamp=row['timestamp'],
                history=history_items,
                rating=_scale_rating(row['rating']),
                message=row['message']
            )
        except ValidationError as e:
            print(f"Error validating row {index}: {e}")
            raise e

    return True


if __name__ == "__main__":

    # Sample
    sample = Sample()
    if check_sample(sample=sample):
        print(f"The sample is correct!")
    else:
        print(f"ERROR: The sample is NOT correct!")
    
    # Dataset    
    dataset_path = DATASET_PATH
    if check_dataset(dataset_path=dataset_path):
        print(f"The dataset {dataset_path} is correct!")
    else:
        print(f"ERROR: The dataset {dataset_path} is NOT correct!")


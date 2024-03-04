"""This module defines different scoring classes
that can be used in the evaluation. Scorers take a test
and reference string and evaluate a score. There are several
implementations:

- ScorerDummy: random scores based on string length.
- ScorerBERT: BERT-score package is used.
- ScorerSBERT: sentence-transformers is used to compute
text embeddings and then the cosine similarity is computed.

Author: Mikel Sagardia
Date: 2024-02-28
"""
from abc import ABC, abstractmethod
import random
from typing import Tuple
from bert_score import BERTScorer
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from .core import (
    logger
)

SBERT_MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


class AbstractScorer(ABC):
    @abstractmethod
    def score(self, predicted: str, reference: str) -> float:
        """Calculate the score between predicted and reference text."""
        pass


class ScorerDummy(AbstractScorer):
    """This scorer delivers a semi-random float score,
    scaled by the lenth of the predicted and reference strings."""
    def __init__(self, seed: int = 42):
        self._seed = seed
        self._scorer_type = ("dummy", "similarity")

    @property
    def type(self) -> Tuple[str, str]:
        return self._scorer_type

    def score(self, predicted: str, reference: str) -> float:
        try:
            random.seed(self._seed)
            length_difference = abs(len(predicted) - len(reference))
            similarity_score = random.random() / (length_difference + 1)
            return max(similarity_score, 0.0)
        except Exception as e:
            # FIXME: Use explicit error types...
            logger.error(f"Error in Dummy scoring: {e}")
            raise e


class ScorerBERT(AbstractScorer):
    """This scorer uses the BERT-score package
    to compute a score between a predicted and reference string.
    
    For more information:
        https://huggingface.co/spaces/evaluate-metric/bertscore
        https://github.com/Tiiiger/bert_score
    """
    def __init__(self, lang: str = "en", rescale_with_baseline: bool = True):
        self._model = self._load_model(lang, rescale_with_baseline)
        self._scorer_type = ("bert", "f1")

    def _load_model(self, lang: str, rescale_with_baseline: bool) -> BERTScorer:
        return BERTScorer(lang=lang, rescale_with_baseline=rescale_with_baseline)

    @property
    def type(self) -> Tuple[str, str]:
        return self._scorer_type

    def score(self, predicted: str, reference: str) -> float:
        try:
            P, R, F1 = self._model.score([predicted], [reference])
            f1 = max(F1.cpu().item(), 0.0)
            return f1
        except Exception as e:
            # FIXME: Use explicit error types...
            logger.error(f"Error in BERT scoring: {e}")
            raise e


class ScorerSBERT(AbstractScorer):
    """This scorer uses the sentence-transformers package
    to compute a score between a predicted and reference string.
    Basically, the embedding vectors of the two strings are computed
    and the the cosine similarity is obtained.
    
    For more information:
        https://huggingface.co/sentence-transformers
        https://www.sbert.net/
    """
    def __init__(self, model_name: str = SBERT_MODEL_NAME):
        self._model = self._load_model(model_name)
        self._scorer_type = ("sbert", "cosine_sim")

    def _load_model(self, model_name: str) -> SentenceTransformer:
        return SentenceTransformer(model_name)

    @property
    def type(self) -> Tuple[str, str]:
        return self._scorer_type

    def score(self, predicted: str, reference: str) -> float:
        try:
            embeddings = self._model.encode([predicted, reference])
            cosine_sim = 1 - cosine(embeddings[0], embeddings[1])
            return max(cosine_sim, 0.0)
        except Exception as e:
            # FIXME: Use explicit error types...            
            logger.error(f"Error in SBERT scoring: {e}")
            raise e


class ScorerLLM(AbstractScorer):
    """This scorer predicts the similarity score between
    a predicted and reference string (answer, in a conversation)
    by asking a LLM.
    
    It needs to be implemented.
    """
    def __init__(self):
        self._scorer_type = ("llm", "float")

    @property
    def type(self) -> Tuple[str, str]:
        return self._scorer_type

    def score(self, predicted: str, reference: str) -> float:
        # TODO: Implement LLM-aided score calculation
        try:
            llm_score = 0.85  # Placeholder for actual LLM score calculation
            return max(llm_score, 0.0)
        except Exception as e:
            # FIXME: Use explicit error types...
            logger.error(f"Error in LLM scoring: {e}")
            raise e

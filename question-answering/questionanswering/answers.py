from typing import Iterable

import numpy
import scipy

from .embeddings import Embedder


_STRING_DTYPE = numpy.dtype("unicode")
_VECTOR_DTYPE = numpy.dtype("float32")
_DEFAULT_LEAF_SIZE = 16


class Answer(object):
    def __init__(self, content: str, question: str, confidence: float) -> None:
        self.content = content
        self.question = question
        self.confidence = confidence

    def to_serializable(self) -> str:
        return {
            **self.__dict__
        }


class AnswerDatabase(object):
    def __init__(self, embedder: Embedder, embedding_size: int = None, answers: numpy.ndarray = None, answer_vectors: numpy.ndarray = None, leaf_size: int = _DEFAULT_LEAF_SIZE) -> None:
        if (answers is None) != (answer_vectors is None):
            raise ValueError("answers and answer_vectors must either both be included or both be excluded!")
        if embedding_size is None and answers is None:
            raise ValueError("Must provide embedding_size if answers/answer_vectors is not provided!")

        self._embedder = embedder
        self._answers = answers if answers is not None else numpy.ndarray(shape=(0,), dtype=_STRING_DTYPE)
        self._answer_vectors = answer_vectors if answer_vectors is not None else numpy.ndarray(shape=(0, embedding_size), dtype=_VECTOR_DTYPE)
        self._leaf_size = leaf_size
        self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answer(self, answer: str) -> None:
        numpy.append(self._answers, answer)
        numpy.append(self._answer_vectors, self.embedder.embed(answer))
        self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answers(self, answers: Iterable[str]) -> None:
        numpy.append(self._answers, answers)
        numpy.append(self._answer_vectors, [self.embedder.embed(answer) for answer in answers])
        self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def save(self, answers_path: str, embedder_path: str) -> None:
        with open(answers_path, "wb") as out_file:
            numpy.savez(out_file, self._answers, self._answer_vectors)
        self._embedder.save(embedder_path)

    @classmethod
    def load(cls, answers_path: str, embedder_path: str) -> "AnswerDatabase":
        with open(answers_path, "rb") as in_file:
            answers, answer_vectors = numpy.load(in_file)
        embedder = Embedder.load()
        return AnswerDatabase(
            embedder=embedder,
            answers=answers,
            answer_vectors=answer_vectors
        )

    @staticmethod
    def _get_confidence(distance: float) -> float:
        # TODO: Normalize and invert this. Smaller distances should give higher confidences.
        return distance

    def get_answer(self, question: str) -> Answer:
        question_vector = self._embedder.embed(question)
        distance, index = self._tree.query(question_vector, k=1)

        content = self._answers[index]
        confidence = AnswerDatabase._get_confidence(distance)

        return Answer(
            content=content,
            question=question,
            confidence=confidence
        )

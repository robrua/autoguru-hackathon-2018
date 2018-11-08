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
        self._answers = answers if answers is not None else numpy.ndarray(shape=(0,1), dtype=_STRING_DTYPE)
        self._answer_vectors = answer_vectors if answer_vectors is not None else numpy.ndarray(shape=(0, embedding_size), dtype=_VECTOR_DTYPE)
        self._leaf_size = leaf_size
        self._embedding_size = embedding_size
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answer(self, answer: str) -> None:
        self._answers = numpy.append(self._answers, answer)
        self._answer_vectors = numpy.append(self._answer_vectors, self._embedder.embed(answer))
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answers(self, answers: Iterable[str]) -> None:
        answers = numpy.asarray(answers, dtype=_STRING_DTYPE).reshape((len(answers),1))
        self._answers = numpy.append(self._answers, answers)
        self._answer_vectors = numpy.append(self._answer_vectors, numpy.asarray([self._embedder.embed(answer) for answer in answers], dtype=_STRING_DTYPE).reshape((len(answers),self._embedding_size)))
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def save(self, answers_path: str, embedder_path: str) -> None:
        with open(answers_path, "wb") as out_file:
            numpy.savez(out_file, answers=self._answers, answer_vectors=self._answer_vectors)
        self._embedder.save(embedder_path)

    @classmethod
    def load(cls, answers_path: str, embedder_path: str) -> "AnswerDatabase":
        # with open(answers_path, "rb") as in_file:
        #     answers_dict = numpy.load(in_file)
        #     answers = answers_dict["answers"]
        #     answer_vectors = answers_dict["answer_vectors"]
        #     print(answer_vectors.shape)
        embedder = Embedder.load(embedder_path)
        return AnswerDatabase(
            embedder=embedder,
            embedding_size=25
            # answers=answers,
            # answer_vectors=answer_vectors
        )

    @staticmethod
    def _get_confidence(distance: float) -> float:
        # TODO: Normalize and invert this. Smaller distances should give higher confidences.
        return distance

    def get_answer(self, question: str) -> Answer:
        try:
            self._tree
        except AttributeError:
            raise ValueError("Must add answers first!")
        question_vector = self._embedder.embed(question)
        distance, index = self._tree.query(question_vector, k=1)

        content = self._answers[index]
        confidence = AnswerDatabase._get_confidence(distance)

        return Answer(
            content=content,
            question=question,
            confidence=confidence
        )

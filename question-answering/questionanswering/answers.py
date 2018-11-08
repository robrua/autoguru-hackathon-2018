from typing import Iterable

import numpy
import scipy
import click

from .embeddings import Embedder


_MAX_ANSWER_LENGTH = 500
_STRING_DTYPE = "<U{}".format(_MAX_ANSWER_LENGTH)
_VECTOR_DTYPE = numpy.dtype("float32")
_DEFAULT_LEAF_SIZE = 16
_DEFAULT_ANSWERS = "answers.txt"
_DEFAULT_DATABASE = "answers.npz"
_DEFAULT_EMBEDDER = "embedder.npz"
_DEFAULT_ENCODING = "UTF-8"


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
        self._answers = answers if answers is not None else numpy.ndarray(shape=(0, 1), dtype=_STRING_DTYPE)
        self._answer_vectors = answer_vectors if answer_vectors is not None else numpy.ndarray(shape=(0, embedding_size), dtype=_VECTOR_DTYPE)
        self._leaf_size = leaf_size
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answer(self, answer: str) -> None:
        answers_array = numpy.ndarray(shape=(1, 1), dtype=self._answers.dtype)
        answer_vectors = numpy.ndarray(shape=(1, self._answer_vectors.shape[1]), dtype=self._answer_vectors.dtype)

        answers_array[0] = answer
        answer_vectors[0] = self._embedder.embed(answer)

        self._answers = numpy.append(self._answers, answers_array)
        self._answer_vectors = numpy.append(self._answer_vectors, answer_vectors)
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answers(self, answers: Iterable[str]) -> None:
        answers_array = numpy.ndarray(shape=(len(answers), 1), dtype=self._answers.dtype)
        answer_vectors = numpy.ndarray(shape=(len(answers), self._answer_vectors.shape[1]), dtype=self._answer_vectors.dtype)

        for i, answer in enumerate(answers):
            answers_array[i] = answer
            answer_vectors[i] = self._embedder.embed(answer)

        self._answers = numpy.append(self._answers, answers_array, axis=0)
        self._answer_vectors = numpy.append(self._answer_vectors, answer_vectors, axis=0)
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def save(self, answers_path: str, embedder_path: str) -> None:
        with open(answers_path, "wb") as out_file:
            numpy.savez(out_file, answers=self._answers, answer_vectors=self._answer_vectors)
        self._embedder.save(embedder_path)

    @classmethod
    def load(cls, answers_path: str, embedder_path: str) -> "AnswerDatabase":
        with open(answers_path, "rb") as in_file:
            answers_dict = numpy.load(in_file)
            answers = answers_dict["answers"]
            answer_vectors = answers_dict["answer_vectors"]
        embedder = Embedder.load(embedder_path)
        return AnswerDatabase(
            embedder=embedder,
            embedding_size=300,
            answers=answers,
            answer_vectors=answer_vectors
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

        content = self._answers[index][0]
        confidence = AnswerDatabase._get_confidence(distance)

        return Answer(
            content=content,
            question=question,
            confidence=confidence
        )


@click.group(help="Create an answer database or answer a question")
def _main() -> None:
    pass


@_main.command(name="create", help="Create an answer database")
@click.option("--answers", "-a", default=_DEFAULT_ANSWERS, help="The file of answers to create a DB of, one answer per line", show_default=True)
@click.option("--database", "-d", default=_DEFAULT_DATABASE, help="The path to create the DB file at", show_default=True)
@click.option("--embedder", "-e", default=_DEFAULT_EMBEDDER, help="The embedder model file path", show_default=True)
@click.option("--encoding", "-e", default=_DEFAULT_ENCODING, help="The text encoding to use when writing the file", show_default=True)
def _create(answers: str = _DEFAULT_ANSWERS, database: str = _DEFAULT_DATABASE, embedder: str = _DEFAULT_EMBEDDER, encoding: str = _DEFAULT_ENCODING) -> None:
    embed = Embedder.load(embedder)

    with open(answers, "r", encoding=encoding) as in_file:
        answers = list(in_file)

    example = embed.embed(answers[0])
    answer_db = AnswerDatabase(embedder=embed, embedding_size=example.shape[0])
    answer_db.add_answers(answers)
    answer_db.save(database, embedder)


@_main.command(name="answer", help="Answer a question")
@click.option("--question", "-q", required=True, type=str, help="The question to answer")
@click.option("--database", "-d", default=_DEFAULT_DATABASE, help="The path to the answer DB file", show_default=True)
@click.option("--embedder", "-e", default=_DEFAULT_EMBEDDER, help="The embedder model file path", show_default=True)
def _answer(question: str, database: str = _DEFAULT_DATABASE, embedder: str = _DEFAULT_EMBEDDER) -> None:
    answer_db = AnswerDatabase.load(database, embedder)
    print(answer_db.get_answer(question).content.strip())


if __name__ == "__main__":
    _main()

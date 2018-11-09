from typing import Iterable, List, Tuple

import numpy
import scipy
import click
import json

from .embeddings import Embedder


_VECTOR_DTYPE = numpy.dtype("float32")
_DEFAULT_LEAF_SIZE = 16
_PAIRWISE_DISTANCE_METRIC = "euclidean"
_DEFAULT_ANSWERS = "question_answers.json"
_DEFAULT_DATABASE = "answers.json"
_DEFAULT_VECTORS = "answer_vectors.npz"
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
    def __init__(self, embedder: Embedder, embedding_size: int = None, question_answer_pairs: List[Tuple[str, str]] = None, vectors: numpy.ndarray = None, leaf_size: int = _DEFAULT_LEAF_SIZE) -> None:
        if (question_answer_pairs is None) != (vectors is None):
            raise ValueError("answers and answer_vectors must either both be included or both be excluded!")
        if embedding_size is None and question_answer_pairs is None:
            raise ValueError("Must provide embedding_size if question_answer_pairs/vectors is not provided!")

        self._embedder = embedder
        self._question_answer_pairs = question_answer_pairs if question_answer_pairs is not None else []
        self._vectors = vectors if vectors is not None else numpy.ndarray(shape=(0, 2, embedding_size), dtype=_VECTOR_DTYPE)
        self._leaf_size = leaf_size
        if self._vectors.shape[0] > 0:
            distances = scipy.spatial.distance.pdist(self._vectors[:, 0, :], metric=_PAIRWISE_DISTANCE_METRIC)
            self._max_distance = numpy.asscalar(distances.max())
            self._tree = scipy.spatial.cKDTree(self._vectors[:, 0, :], leafsize=self._leaf_size)

    def add_answer(self, question: str, answer: str) -> None:
        self._question_answer_pairs.append((question, answer))

        vectors = numpy.ndarray(shape=(1, 2, self._answer_vectors.shape[2]), dtype=self._vectors.dtype)
        vectors[0][0], vectors[0][1] = self._embedder.embed(question), self._embedder.embed(answer)

        self._vectors = numpy.append(self._vectors, vectors, axis=0)
        if self._vectors.shape[0] > 0:
            distances = scipy.spatial.distance.pdist(self._vectors[:, 0, :], metric=_PAIRWISE_DISTANCE_METRIC)
            self._max_distance = numpy.asscalar(distances.max())
            self._tree = scipy.spatial.cKDTree(self._vectors[:, 0, :], leafsize=self._leaf_size)

    def add_answers(self, question_answer_pairs: Iterable[Tuple[str, str]]) -> None:
        vectors = numpy.ndarray(shape=(len(question_answer_pairs), 2, self._vectors.shape[2]), dtype=self._vectors.dtype)

        for i, pair in enumerate(question_answer_pairs):
            self._question_answer_pairs.append(pair)
            vectors[i][0], vectors[i][1] = self._embedder.embed(pair[0]), self._embedder.embed(pair[1])

        self._vectors = numpy.append(self._vectors, vectors, axis=0)
        if self._vectors.shape[0] > 0:
            distances = scipy.spatial.distance.pdist(self._vectors[:, 0, :], metric=_PAIRWISE_DISTANCE_METRIC)
            self._max_distance = numpy.asscalar(distances.max())
            self._tree = scipy.spatial.cKDTree(self._vectors[:, 0, :], leafsize=self._leaf_size)

    def save(self, answers_path: str = _DEFAULT_DATABASE, vectors_path: str = _DEFAULT_VECTORS, embedder_path: str = _DEFAULT_EMBEDDER, encoding: str = _DEFAULT_ENCODING) -> None:
        with open(vectors_path, "wb") as out_file:
            numpy.save(out_file, self._vectors)
        with open(answers_path, "w", encoding=encoding) as out_file:
            json.dump(self._question_answer_pairs, out_file)

        self._embedder.save(embedder_path)

    @classmethod
    def load(cls, answers_path: str = _DEFAULT_DATABASE, vectors_path: str = _DEFAULT_VECTORS, embedder_path: str = _DEFAULT_EMBEDDER, encoding: str = _DEFAULT_ENCODING) -> "AnswerDatabase":
        with open(answers_path, "r", encoding=encoding) as in_file:
            question_answer_pairs = json.load(in_file)
        with open(vectors_path, "rb") as in_file:
            vectors = numpy.load(in_file)
        embedder = Embedder.load(embedder_path)
        return AnswerDatabase(
            embedder=embedder,
            question_answer_pairs=question_answer_pairs,
            vectors=vectors
        )

    def _get_confidence(self, distance: float) -> float:
        return 1.0 - (distance / self._max_distance)

    def get_answer(self, question: str) -> Answer:
        try:
            self._tree
        except AttributeError:
            raise ValueError("Must add answers first!")

        question_vector = self._embedder.embed(question)
        distance, index = self._tree.query(question_vector, k=1)

        content = self._question_answer_pairs[index][1]
        confidence = self._get_confidence(distance)

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
@click.option("--vectors", "-v", default=_DEFAULT_VECTORS, help="The path to put the question/answer vectors", show_default=True)
@click.option("--embedder", "-e", default=_DEFAULT_EMBEDDER, help="The embedder model file path", show_default=True)
@click.option("--encoding", "-c", default=_DEFAULT_ENCODING, help="The text encoding to use when writing the file", show_default=True)
def _create(answers: str = _DEFAULT_ANSWERS, database: str = _DEFAULT_DATABASE, vectors: str = _DEFAULT_VECTORS, embedder: str = _DEFAULT_EMBEDDER, encoding: str = _DEFAULT_ENCODING) -> None:
    embed = Embedder.load(embedder)

    with open(answers, "r", encoding=encoding) as in_file:
        answers = json.load(in_file)

    example = embed.embed(next(iter(answers.keys())))
    answer_db = AnswerDatabase(embedder=embed, embedding_size=example.shape[0])
    answer_db.add_answers([(question, answer) for question, answer in answers.items()])
    answer_db.save(database, vectors, embedder)


@_main.command(name="answer", help="Answer a question")
@click.option("--question", "-q", required=True, type=str, help="The question to answer")
@click.option("--database", "-d", default=_DEFAULT_DATABASE, help="The path to the answer DB file", show_default=True)
@click.option("--vectors", "-v", default=_DEFAULT_VECTORS, help="The path to the question/answer vectors", show_default=True)
@click.option("--embedder", "-e", default=_DEFAULT_EMBEDDER, help="The embedder model file path", show_default=True)
def _answer(question: str, database: str = _DEFAULT_DATABASE, vectors: str = _DEFAULT_VECTORS, embedder: str = _DEFAULT_EMBEDDER) -> None:
    answer_db = AnswerDatabase.load(database, vectors, embedder)
    answer = answer_db.get_answer(question)
    print("{} - {}".format(answer.content, answer.confidence))


if __name__ == "__main__":
    _main()

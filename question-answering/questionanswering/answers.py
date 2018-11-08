from typing import Iterable

import numpy as np
import scipy

from .embeddings import Embedder


_MAX_ANSWER_LENGTH = 500
_STRING_DTYPE = "<U{}".format(_MAX_ANSWER_LENGTH)
_VECTOR_DTYPE = np.dtype("float32")
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
    def __init__(self, embedder: Embedder, embedding_size: int = None, answers: np.ndarray = None, answer_vectors: np.ndarray = None, leaf_size: int = _DEFAULT_LEAF_SIZE) -> None:
        if (answers is None) != (answer_vectors is None):
            raise ValueError("answers and answer_vectors must either both be included or both be excluded!")
        if embedding_size is None and answers is None:
            raise ValueError("Must provide embedding_size if answers/answer_vectors is not provided!")

        self._embedder = embedder
        self._answers = answers if answers is not None else np.ndarray(shape=(0, 1), dtype=_STRING_DTYPE)
        self._answer_vectors = answer_vectors if answer_vectors is not None else np.ndarray(shape=(0, embedding_size), dtype=_VECTOR_DTYPE)
        self._leaf_size = leaf_size
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answer(self, answer: str) -> None:
        answers_array = np.ndarray(shape=(1, 1), dtype=self._answers.dtype)
        answer_vectors = np.ndarray(shape=(1, self._answer_vectors.shape[1]), dtype=self._answer_vectors.dtype)

        answers_array[0] = answer
        answer_vectors[0] = self._embedder.embed(answer)

        self._answers = np.append(self._answers, answers_array)
        self._answer_vectors = np.append(self._answer_vectors, answer_vectors)
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def add_answers(self, answers: Iterable[str]) -> None:
        answers_array = np.ndarray(shape=(len(answers), 1), dtype=self._answers.dtype)
        answer_vectors = np.ndarray(shape=(len(answers), self._answer_vectors.shape[1]), dtype=self._answer_vectors.dtype)

        for i, answer in enumerate(answers):
            answers_array[i] = answer
            answer_vectors[i] = self._embedder.embed(answer)

        self._answers = np.append(self._answers, answers_array, axis=0)
        self._answer_vectors = np.append(self._answer_vectors, answer_vectors, axis=0)
        if self._answer_vectors.shape[0] > 0:
            self._tree = scipy.spatial.cKDTree(self._answer_vectors, leafsize=self._leaf_size)

    def save(self, answers_path: str, embedder_path: str) -> None:
        with open(answers_path, "wb") as out_file:
            np.savez(out_file, answers=self._answers, answer_vectors=self._answer_vectors)
        self._embedder.save(embedder_path)

    @classmethod
    def load(cls, answers_path: str, embedder_path: str) -> "AnswerDatabase":
        with open(answers_path, "rb") as in_file:
            answers_dict = np.load(in_file)
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
        if question_vector.shape == tuple():
            distance = np.inf
            content = "What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \"clever\" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You're fucking dead, kiddo."
        else:
            distance, index = self._tree.query(question_vector, k=1)
            content = self._answers[index][0]

        confidence = AnswerDatabase._get_confidence(distance)

        return Answer(
            content=content,
            question=question,
            confidence=confidence
        )

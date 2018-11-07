from typing import Iterable

import numpy


class Embedder(object):
    def __init__(self) -> None:
        pass

    def add_corpus(corpus: Iterable[str]) -> None:
        pass

    def embed(text: str) -> numpy.ndarray:
        pass

    def save(self, filepath: str) -> None:
        pass

    @classmethod
    def load(filepath: str) -> "Embedder":
        pass

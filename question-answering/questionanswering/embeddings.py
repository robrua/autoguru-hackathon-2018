from typing import Iterable

import gensim.downloader as api
import numpy

class Embedder(object):
    def __init__(self) -> None:
        # self.model = api.load("word2vec-google-news-300")
        self.model = api.load("glove-twitter-25")

    def _combine(self, vectors: list):
        return numpy.average(vectors, axis=0)

    def add_corpus(self, corpus: Iterable[str]) -> None:
        pass

    def embed(self, text: str) -> numpy.ndarray:
        # Create a set of frequent words
        stoplist = set('for a of the and to in'.split(' '))
        # Lowercase each document, split it by white space and filter out stopwords
        words = [word for word in text.lower().split() if word not in stoplist]
        vectors = [self.model.wv[word] for word in words]
        return self._combine(vectors)

    def save(self, filepath: str) -> None:
        pass

    @classmethod
    def load(filepath: str) -> "Embedder":
        pass

if __name__ == "__main__":
    embedder = Embedder()
    print(embedder.embed('taco bell is a restaurant'))

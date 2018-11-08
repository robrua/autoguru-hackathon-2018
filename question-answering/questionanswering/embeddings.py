from typing import Iterable, List

from gensim.parsing.preprocessing import preprocess_string, strip_tags, strip_punctuation, strip_multiple_whitespaces, remove_stopwords, stem_text
from gensim.models import KeyedVectors
import gensim.downloader as api
import numpy
import click


_DEFAULT_SEED_MODEL = "glove-twitter-25"  # "word2vec-google-news-300"
_DEFAULT_MODEL = "model.npz"
_PREPROCESSING_FILTERS = [
    lambda x: x.lower(),
    strip_tags,
    strip_punctuation,
    strip_multiple_whitespaces,
    remove_stopwords,
    stem_text
]


class Embedder(object):
    def __init__(self, model: KeyedVectors) -> None:
        self._model = model

    @staticmethod
    def _combine(vectors: List[numpy.ndarray]) -> numpy.ndarray:
        return numpy.average(vectors, axis=0)

    def add_corpus(self, corpus: Iterable[str]) -> None:
        pass

    def embed(self, text: str) -> numpy.ndarray:
        tokens = preprocess_string(text, _PREPROCESSING_FILTERS)
        vectors = []
        for token in tokens:
            try:
                vectors.append(self._model.wv[token])
            except KeyError:
                continue
        return Embedder._combine(vectors)

    def save(self, filepath: str) -> None:
        with open(filepath, "wb") as out_file:
            self._model.save(out_file)

    @classmethod
    def load(cls, filepath: str) -> "Embedder":
        model = KeyedVectors.load(filepath)
        return Embedder(
            model=model
        )


@click.group(help="Train or evaluate word embeddings")
def _main() -> None:
    pass


@_main.command(name="evaluate", help="Evaluate word embeddings for an existing model")
@click.option("--text", "-t", required=True, type=str, help="The text to evaluate")
@click.option("--model", "-m", default=_DEFAULT_MODEL, help="The model file to evaluate with", show_default=True)
def _evaluate(text: str, model: str = _DEFAULT_MODEL) -> None:
    embedder = Embedder.load(model)
    print(embedder.embed(text))


@_main.command(name="train", help="Train word embeddings")
@click.option("--data", "-d", required=True, type=str, help="The path to the data to train with on disk")
@click.option("--model", "-m", default=_DEFAULT_MODEL, help="The model file to save the model to", show_default=True)
@click.option("--seed", "-s", default=_DEFAULT_SEED_MODEL, help="The seed gensim model to use for training", show_default=True)
def _train(data: str, model: str = _DEFAULT_MODEL, seed: str = _DEFAULT_SEED_MODEL) -> None:
    seed = api.load(seed)
    # TODO: actually train
    embedder = Embedder(model=seed)
    embedder.save(model)


if __name__ == "__main__":
    _main()

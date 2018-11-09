from typing import List

from gensim.parsing.preprocessing import preprocess_string, strip_tags, strip_punctuation, strip_multiple_whitespaces, remove_stopwords
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
from sklearn.preprocessing import normalize
import gensim.downloader as api
import numpy
import click


_DEFAULT_DATASET = "text8"
_DEFAULT_MODEL = "embedder.npz"
_DEFAULT_DATA_OUT = "dataset.txt"
_DEFAULT_DATA_IN = "data.txt"
_DEFAULT_ENCODING = "UTF-8"
_DEFAULT_EMBEDDING_SIZE = 300
_DEFAULT_GRAM_SIZE = 5
_DEFAULT_MIN_COUNT = 5
_DEFAULT_WORKERS = 3
_DEFAULT_SKIPGRAM = False
_DEFAULT_HIERARCHICAL_SOFTMAX = False
_DEFAULT_NEGATIVE_SAMPLES = 5
_PREPROCESSING_FILTERS = [
    lambda x: x.lower(),
    strip_tags,
    strip_punctuation,
    strip_multiple_whitespaces,
    remove_stopwords
]


class Embedder(object):
    def __init__(self, model: KeyedVectors) -> None:
        self._model = model

    @staticmethod
    def _combine(vectors: List[numpy.ndarray]) -> numpy.ndarray:
        mean = numpy.average(vectors, axis=0)
        return normalize(mean.reshape((1, mean.shape[0]))).reshape(mean.shape)

    @classmethod
    def train(cls,
              corpus: str,
              embedding_size: int = _DEFAULT_EMBEDDING_SIZE,
              gram_size: int = _DEFAULT_GRAM_SIZE,
              min_count: int = _DEFAULT_MIN_COUNT,
              workers: int = _DEFAULT_WORKERS,
              skipgram: bool = _DEFAULT_SKIPGRAM,
              hierarchical_softmax: bool = _DEFAULT_HIERARCHICAL_SOFTMAX,
              negative_samples: int = _DEFAULT_NEGATIVE_SAMPLES) -> "Embedder":
        model = Word2Vec(
            corpus_file=corpus,
            size=embedding_size,
            window=gram_size,
            min_count=min_count,
            workers=workers,
            sg=int(skipgram),
            hs=int(hierarchical_softmax),
            negative=negative_samples
        )
        return Embedder(model.wv)

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
@click.option("--data", "-d", default=_DEFAULT_DATA_OUT, help="The path to the data to train with on disk", show_default=True)
@click.option("--model", "-m", default=_DEFAULT_MODEL, help="The model file to save the model to", show_default=True)
def _train(data: str, model: str = _DEFAULT_MODEL) -> None:
    embedder = Embedder.train(data)
    embedder.save(model)


@_main.command(name="download", help="Download a word embedding dataset")
@click.option("--name", "-n", default=_DEFAULT_DATASET, help="The name of the dataset to download from gensim", show_default=True)
@click.option("--out", "-o", default=_DEFAULT_DATA_OUT, help="The file to save the dataset to", show_default=True)
@click.option("--encoding", "-e", default=_DEFAULT_ENCODING, help="The text encoding to use when writing the file", show_default=True)
def _download(name: str = _DEFAULT_DATASET, out: str = _DEFAULT_DATA_OUT, encoding: str = _DEFAULT_ENCODING) -> None:
    dataset = api.load(name)
    with open(out, "w", encoding=encoding) as out_file:
        for tokens in dataset:
            out_file.write("{}\n".format("\t".join(tokens)))


@_main.command("append", help="Append data to a word embedding dataset")
@click.option("--data", "-d", default=_DEFAULT_DATA_IN, help="The data to add to the dataset, with one message per line", show_default=True)
@click.option("--dataset", "-s", default=_DEFAULT_DATA_OUT, help="The dataset to add the data to", show_default=True)
@click.option("--encoding", "-e", default=_DEFAULT_ENCODING, help="The text encoding to use when writing the file", show_default=True)
def _append(data: str = _DEFAULT_DATA_IN, dataset: str = _DEFAULT_DATA_OUT, encoding: str = _DEFAULT_ENCODING) -> None:
    with open(data, "r", encoding=encoding) as in_file, open(dataset, "a", encoding=encoding) as out_file:
        for line in in_file:
            tokens = preprocess_string(line, _PREPROCESSING_FILTERS)
            out_file.write("{}\n".format("\t".join(tokens)))


if __name__ == "__main__":
    _main()

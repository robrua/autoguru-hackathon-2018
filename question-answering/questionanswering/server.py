from typing import Dict, Any
import json

from faker import Faker
import random
import bottle
import click

from .answers import AnswerDatabase, Answer


_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 41170
_DEFAULT_SERVER = "paste"
_DEFAULT_DEBUG = False
_DEFAULT_EMBEDDER = "embedder.npz"
_DEFAULT_ANSWERS = "answers.npz"


def _initialize_services(application: bottle.Bottle, answer_database: AnswerDatabase) -> None:
    @application.hook("after_request")
    def _enable_cors() -> None:
        bottle.response.headers["Access-Control-Allow-Origin"] = "*"
        bottle.response.headers["Access-Control-Allow-Methods"] = "PUT, GET, POST, DELETE, OPTIONS"
        bottle.response.headers["Access-Control-Allow-Headers"] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
        bottle.response.headers["Access-Control-Max-Age"] = "3600"

    @application.post("/autoguru/answer-stub")
    def _answer_stub() -> Dict[str, Any]:
        try:
            query = json.load(bottle.request.body)
        except json.decoder.JSONDecodeError:
            return bottle.HTTPError(status=500, body="Failed to decode JSON POST data!")

        try:
            question = query["question"]
        except KeyError:
            return bottle.HTTPError(status=400, body="POST request included no \"question\" field!")

        fake = Faker()
        return Answer(
            content=fake.text(),
            question=question,
            confidence=random.uniform(0.0, 1.0)
        ).to_serializable()

    @application.post("/autoguru/answer")
    def _answer() -> Dict[str, Any]:
        try:
            query = json.load(bottle.request.body)
        except json.decoder.JSONDecodeError as e:
            return bottle.HTTPError(status=500, body="Failed to decode JSON POST data!", exception=e)

        try:
            question = query["question"]
        except KeyError:
            return bottle.HTTPError(status=400, body="POST request included no \"question\" field!")

        return answer_database.get_answer(question).to_serializable()


@click.command(name="run", help="Run the AutoGuru Question Answering REST services")
@click.option("--host", "-h", default=_DEFAULT_HOST, help="The host IP to bind the server on", show_default=True)
@click.option("--port", "-p", default=_DEFAULT_PORT, help="The port to bind the server on", show_default=True)
@click.option("--server", "-s", default=_DEFAULT_SERVER, help="The WSGI web server to run on", show_default=True)
@click.option("--embedder", "-e", default=_DEFAULT_EMBEDDER, help="The path to the word embedder model", show_default=True)
@click.option("--answers", "-a", default=_DEFAULT_ANSWERS, help="The path to the answer corpus", show_default=True)
@click.option("--debug/--live", "-d/-l", default=_DEFAULT_DEBUG, help="Whether to include debug logs in the server output", show_default=True)
def _run(host: str = _DEFAULT_HOST,
         port: int = _DEFAULT_PORT,
         server: str = _DEFAULT_SERVER,
         embedder: str = _DEFAULT_EMBEDDER,
         answers: str = _DEFAULT_ANSWERS,
         debug: bool = _DEFAULT_DEBUG) -> None:
    answer_database = AnswerDatabase.load(answers_path=answers, embedder_path=embedder)

    application = bottle.Bottle()
    _initialize_services(application, answer_database)

    application.run(host=host, port=port, server=server, debug=debug)


if __name__ == "__main__":
    _run()

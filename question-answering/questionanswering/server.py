import click
import bottle


_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 41170
_DEFAULT_SERVER = "paste"
_DEFAULT_DEBUG = False


@bottle.get("/autoguru/hello/<name>")
def _hello(name: str) -> str:
    return "Hello, {}!".format(name)


@bottle.hook("after_request")
def _enable_cors() -> None:
    bottle.response.headers["Access-Control-Allow-Origin"] = "*"
    bottle.response.headers["Access-Control-Allow-Methods"] = "PUT, GET, POST, DELETE, OPTIONS"
    bottle.response.headers["Access-Control-Allow-Headers"] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
    bottle.response.headers["Access-Control-Max-Age"] = "3600"


@click.command(name="run", help="Run the AutoGuru Question Answering REST services")
@click.option("--host", "-h", default=_DEFAULT_HOST, help="The host IP to bind the server on", show_default=True)
@click.option("--port", "-p", default=_DEFAULT_PORT, help="The port to bind the server on", show_default=True)
@click.option("--server", "-s", default=_DEFAULT_SERVER, help="The WSGI web server to run on", show_default=True)
@click.option("--debug/--live", "-d/-l", default=_DEFAULT_DEBUG, help="Whether to include debug logs in the server output", show_default=True)
def _run(host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT, server: str = _DEFAULT_SERVER, debug: bool = _DEFAULT_DEBUG) -> None:
    bottle.run(host=host, port=port, server=server, debug=debug)


if __name__ == "__main__":
    _run()

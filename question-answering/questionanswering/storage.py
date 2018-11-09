from typing import Any

import json

class Storage(object):
    def __init__(self, filepath: str) -> None:
        with open(filepath) as in_file:
            self._data = json.load(in_file)

    def _save(self) -> None:
        with open('storage.json', 'w') as outfile:
            json.dump(self._data, outfile)

    def _load(self) -> object:
        with open('storage.json') as in_file:
            return json.load(in_file)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def get(self, key: str) -> Any:
        return self._data[key]

    def increment_key(self, key: str) -> None:
        value = self.get(key)
        value += 1
        self.set(key, value)

    def push(self, key: str, value: Any) -> None:
        value = self.get(key)
        value.push(value)
        self.set(key, value)

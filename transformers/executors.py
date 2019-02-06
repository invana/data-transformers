# Created by venkataramana on 04/02/19.
import json

from pymongo import MongoClient


class Executor:
    def connect(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError


class ReadFromFile(Executor):
    def __init__(self, file_path):
        self._file_path = file_path

    def read(self):
        with open(self._file_path) as fp:
            data = json.load(fp)
            fp.close()
        return data

    def disconnect(self):
        pass

    def connect(self):
        pass


class ReadFromMongo(Executor):
    def __init__(self, connection_string, db, collection, query=None, fields=None):
        self._connection_string = connection_string
        self._db = db
        self._collection = collection
        self._query = query
        self._fields = fields
        self._client = None

    def connect(self):
        self._client = MongoClient(self._connection_string)

    def read(self):
        if isinstance(self._client, MongoClient):
            for doc in self._client[self._db][self._collection].find(self._query, projection=self._fields):
                yield doc

    def disconnect(self):
        if isinstance(self._client, MongoClient):
            self._client.close()


class WriteToFile(Executor):
    def write(self, objects, file_name):
        with open(file_name, 'w') as fp:
            json.dump(objects, fp)
            fp.close()

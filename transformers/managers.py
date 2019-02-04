# Created by venkataramana on 04/02/19.
from copy import deepcopy


class OTBase:
    """
        Object Transformer Base class

        Arguments
        ---------
        include - fields to include or mapping config for json bender

    """

    def __init__(self, include=None):
        self.include = include

    def expand(self, objects):
        raise NotImplementedError


class OTConf:
    """
        Object Transformer config class

        Arguments
        ---------

        key_path - dot notation of specific field
        cls - Transform class that need to be applied

    """

    def __init__(self, key_path, cls, *args, **kwargs):
        self.key_path = key_path
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def clone(self):
        return deepcopy(self)


class OTManager:
    """
        Object Transform Manager Renders the output into required form

        Arguments
        ---------

        ops - list of OTConf objects

    """

    def __init__(self, ops):
        self._ops = ops
        self.results = []

    def _sub_process(self, op, _object):
        if op.key_path in _object:
            op.cls(op.key_path, *op.args, **op.kwargs).process(_object)
        elif '.' in op.key_path:
            key_split = op.key_path.split('.')
            _op = op.clone()
            _op.key_path = '.'.join(key_split[1:])
            if isinstance(_object[key_split[0]], list):
                for _list_item in _object[key_split[0]]:
                    self._sub_process(_op, _list_item)
            else:
                self._sub_process(_op, _object[key_split[0]])
        return _object

    def process(self, executor):
        for _object in executor.read():
            for op in self._ops:
                self._sub_process(op, _object)
            self.results.append(_object)
        return self

    def print(self):
        for _object in self.results:
            for item in _object['items']:
                print('item', item)

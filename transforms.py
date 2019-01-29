# Created by venkataramana on 29/01/19.
import re
from copy import deepcopy
from urllib import parse


class FTBase:
    """
        Field Transformer Base class
    """

    def __init__(self, key, *args, **kwargs):
        self._key = key

    def process(self, element):
        raise NotImplementedError


class UrlDomainTransformer(FTBase):
    """
        Url Domain name Transformer

    """

    def process(self, element):
        if element is None:
            return
        url = element.get(self._key, None)
        if isinstance(url, str):
            element.update({self._key: parse.urlparse(url).netloc})


class FloatTransform(FTBase):
    """
        Integer Transformer

        string examples:
            works with: '1234.123'
            not works:  '$1234.123'
    """

    def process(self, element):
        val = element.get(self._key, None)
        if isinstance(val, float):
            element.update({self._key: val})
        if isinstance(val, str) or isinstance(val, int):
            element.update({self._key: float(val)})
        else:
            raise KeyError


class IntTransform(FTBase):
    """
        Integer Transformer

        string examples:
            works with: '1234'
            not works:  '$1234'
    """

    def process(self, element):
        val = element.get(self._key, None)
        if isinstance(val, int):
            element.update({self._key: val})
        if isinstance(val, str) or isinstance(val, float):
            element.update({self._key: int(val)})
        else:
            raise KeyError


class RegexTransform(FTBase):
    def __init__(self, key, regex=None, *args, **kwargs):
        super(RegexTransform, self).__init__(key)
        self._regex = regex or kwargs.get('regex', None) or '(\d+\.\d+)'

    def process(self, element):
        val = element[self._key]
        if isinstance(val, str) or isinstance(val, bytes):
            element.update({self._key: re.findall(self._regex, val)})
        else:
            raise RuntimeError("Element value type expected string or bytes-like object")


class OTBase:
    def __init__(self, key=None):
        self._key = key

    def expand(self, objects):
        raise NotImplementedError


class ListIterator(OTBase):
    def expand(self, objects):
        for _object in objects[self._key] if self._key else objects:
            yield _object


class OTConf:
    def __init__(self, key_path, cls, *args, **kwargs):
        self.key_path = key_path
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def clone(self):
        return deepcopy(self)


class OTManager:
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


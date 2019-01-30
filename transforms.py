# Created by venkataramana on 29/01/19.
import re
from copy import deepcopy
from urllib import parse


class FTBase:
    """
        Field Transformer Base class

        Arguments
        ----------

        key - key in an object

        Keyword Arguments
        -----------------

        update_element - Boolean value
        update_key - Update element key

        >>>
            if update_element is True updates the transformed value on the element, if update_key is given it updates
            the value with this update_key on element (which might add new key on element) else updates the same key.
    """

    def __init__(self, key, *args, **kwargs):
        self._key = key
        self._update_element = kwargs.get('update_element')
        self._update_key = kwargs.get('update_key')

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
            domain = parse.urlparse(url).netloc
            if self._update_element:
                element.update({self._update_key if self._update_key else self._key: domain})
            else:
                return domain


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
            if not self._update_element:
                return val
        if isinstance(val, str) or isinstance(val, int):
            val = float(val)
            if self._update_element:
                element.update({self._update_key if self._update_key else self._key: val})
            else:
                return val
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
            if not self._update_element:
                return val
        if isinstance(val, str) or isinstance(val, float):
            val = int(val)
            if self._update_element:
                element.update({self._update_key if self._update_key else self._key: val})
            else:
                return val
        else:
            raise KeyError


class RegexTransform(FTBase):
    def __init__(self, key, regex=None, *args, **kwargs):
        super(RegexTransform, self).__init__(key, *args, **kwargs)
        self._regex = regex or kwargs.get('regex', None) or '(\d+\.\d+)'

    def process(self, element):
        val = element[self._key]
        if isinstance(val, str) or isinstance(val, bytes):
            val = re.findall(self._regex, val)
            if self._update_element:
                element.update({self._update_key if self._update_key else self._key: val})
            else:
                return val
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

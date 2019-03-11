# Created by venkataramana on 29/01/19.
import json
import re
from copy import deepcopy
from urllib import parse

from jsonbender import bend, S, Context
from jsonbender.list_ops import ForallBend
from slugify import slugify


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


class SlugField(FTBase):
    """
        Integer Transformer

        Transform the given value into slug type

        string examples:
            works with: '1234.123'
            not works:  '$1234.123'
    """

    def process(self, element):
        val = element.get(self._key, None)
        return slugify(val)


class UrlDomainTransformer(FTBase):
    """
        Url Domain name Transformer

        Transforms the given url into domain name

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

        Transform the given value into float type

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

        Transforms the given value into int type

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
    """
        Regular Expression Transformer

        Transforms the given value by applying the given regular expression

    """

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


class OutputRenderer(OTBase):
    """
        Renders the output into required form

        Arguments
        ---------

        inherits super class methods

    """

    def _projection(self, _object, _keys):
        return {key: _object.get(key, None) for key in _keys}

    def _list_projection(self, _list, _keys):
        return [self._projection(item, _keys) for item in _list]

    @staticmethod
    def _parse_keys_to_dict(keys):
        _keys_dict = {}
        for key in keys:
            if '.' not in key:
                _keys_dict.update({key: 0})
            else:
                key1, key2 = key.split('.')
                if key1 in _keys_dict:
                    _keys_dict[key1].append(key2)
                else:
                    _keys_dict.update({key1: [key2]})
        return _keys_dict

    def _sub_expand(self, _object, keys):
        """
        >>>
            {
                'client_info':0
                'items':['url','title','description','item_no']
            }
        """
        keys_dict = self._parse_keys_to_dict(keys)
        result = []
        _new_object = {}
        _new_objects = []
        for key in keys_dict:
            if keys_dict[key] is 0:
                _new_object.update(self._projection(_object, [key]))
            elif isinstance(keys_dict[key], list):
                _new_objects += self._list_projection(_object[key], keys_dict[key])
        for _new_obj in _new_objects:
            _new_obj.update(_new_object)
        return _new_objects

    def expand(self, objects):
        results = []
        for _object in objects:
            results += self._sub_expand(_object, self.include)
        return results


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


class OutputBender(OTBase):
    """
        Output Bender Render the output into required form using jsonbender.

        Arguments
        ---------

        include - json bender mapping config

    """

    def expand(self, objects):
        if isinstance(self.include, list):
            if self.include.__len__() == 0:
                raise ValueError('include should not empty')
            for item in self.include:
                if isinstance(item, dict):
                    if '_$' not in item:
                        raise KeyError("_$ not exist in include item")
                else:
                    raise ValueError('item must of dict type')
        else:
            raise TypeError('include must be list')
        if not isinstance(objects, list):
            raise ValueError("objects must be list")
        return [[bend(_mapping['_$'], _object, context=_object) for _object in objects] for _mapping in self.include]


class JsonBenderConfParser:
    """
        JsonBenderConfParser parses the given conf and converts it into an actual jsonbender mapping config.

        Arguments
        ---------

        file_path - file path to json config file

    """

    def __init__(self, file_path):
        self.file_path = file_path

    def get_json_conf(self):
        with open(self.file_path) as fp:
            _json_conf = json.load(fp)
            fp.close()
            return _json_conf

    @staticmethod
    def _get_mapping_cls(_str):
        MAPPING_CLS = {
            "__S": S,
            "__ForallBend": ForallBend,
            "__Context": Context
        }
        return MAPPING_CLS.get(_str, None)

    def _parse_object(self, _object):
        if '_pipe' not in _object:
            raise AttributeError("_pipe key is missing")
        _object = _object['_pipe']
        _pipe = None
        for op in _object:
            attrs = {}
            cls = self._get_mapping_cls(op['class'])
            if isinstance(op['attrs'], list):
                for attrs in op['attrs']:
                    if not isinstance(attrs, str):
                        raise ValueError("attrs must be string")
                attrs = op['attrs']
            elif isinstance(op['attrs'], dict):
                for key in op['attrs']:
                    _sub_object = op['attrs'][key]
                    if '_pipe' in _sub_object:
                        attrs.update({key: self._parse_object(_sub_object)})
                    else:
                        _sub_cls = self._get_mapping_cls(op['attrs'][key]['class'])
                        _sub_cls_obj = _sub_cls(*op['attrs'][key]['attrs'])
                        attrs.update(
                            {key: _sub_cls_obj})
                attrs = [attrs]
            _pipe = cls(*attrs) if not _pipe else _pipe.__rshift__(cls(*attrs))
        return _pipe

    def parse(self):
        _json_conf = self.get_json_conf()
        _mapping = []

        for _object in _json_conf:
            if not isinstance(_object, dict):
                raise ValueError("Array item must be object type")
            elif '_$' not in _object:
                raise ValueError("Array item must have _$ key")
            else:
                _mapping.append({'_$': self._parse_object(_object['_$'])})
        return _mapping

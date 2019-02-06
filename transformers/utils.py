# Created by venkataramana on 04/02/19.
import json

from jsonbender import Context, S
from jsonbender.list_ops import ForallBend


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

# Created by venkataramana on 04/02/19.
from jsonbender import bend
from transformers.managers import OTBase


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

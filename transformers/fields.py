# Created by venkataramana on 04/02/19.
import re
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

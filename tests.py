# Created by venkataramana on 29/01/19.
import unittest
from unittest import TestCase
import json

from jsonbender import S, Context
from jsonbender.list_ops import ForallBend

from executors import ReadFromFile, ReadFromMongo, WriteToFile
from transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager, OutputRenderer, \
    OutputBender, JsonBenderConfParser


class ReadFromFileTest(TestCase):

    def testSample(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        result = OTManager(ops).process(file_executor).results
        with open('samples/tests_results_expected/sample1.json') as fp:
            expected = json.load(fp)
            fp.close()
        self.assertListEqual(result, expected)


class ReadFromMongoTest(TestCase):
    def _(self):
        mongo_executor = ReadFromMongo('mongodb://10.1.0.83:27017/crawler_data', 'crawler_data', 'website_data')
        mongo_executor.connect()
        ops = [OTConf('items.url', UrlDomainTransformer), OTConf('items.item_no', FloatTransform),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})')]
        results = OTManager(ops).process(mongo_executor).results
        with open('samples/tests_results_expected/sample2.json') as fp:
            expected = json.load(fp)
            fp.close()
        mongo_executor.disconnect()
        self.assertListEqual(results, expected)


class OutputRendererTest(TestCase):
    def testSample(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        ot_manager = OTManager(ops).process(file_executor)
        results = OutputRenderer(
            include=['client_info', 'items.url', 'items.title', 'items.description', 'items.item_no']).expand(
            ot_manager.results)
        with open('samples/tests_results_expected/sample3.json') as fp:
            expected = json.load(fp)
            fp.close()
        self.assertListEqual(results, expected)


class OutputBenderTest(TestCase):
    def testSample(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        ot_manager = OTManager(ops).process(file_executor)
        MAPPING = [
            {
                '_$': S('items') >> ForallBend({
                    'url': S('url'),
                    'title': S('title'),
                    'description': S('description'),
                    'item_no': S('item_no'),
                    'client_info': Context() >> S('client_info')
                })
            }
        ]
        results = OutputBender(include=MAPPING).expand(ot_manager.results)
        file_executor = ReadFromFile('samples/tests_results_expected/sample4.json')
        expected = file_executor.read()
        self.assertListEqual(results, expected)


class JsonBenderConfParserTest(TestCase):
    def testSample(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        ot_manager = OTManager(ops).process(file_executor)
        MAPPING = JsonBenderConfParser('samples/confs/bender_conf.json').parse()
        results = OutputBender(include=MAPPING).expand(ot_manager.results)
        file_executor = ReadFromFile('samples/tests_results_expected/sample5.json')
        expected = file_executor.read()
        self.assertListEqual(results, expected)


if __name__ == '__main__':
    unittest.main()

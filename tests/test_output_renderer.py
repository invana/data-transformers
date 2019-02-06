# Created by venkataramana on 29/01/19.
import unittest
from unittest import TestCase
import json

from transformers.executors import ReadFromFile
from transformers.transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager, \
    OutputRenderer


class OutputRendererTest(TestCase):
    maxDiff = None

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


if __name__ == '__main__':
    unittest.main()

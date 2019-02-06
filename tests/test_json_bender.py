# Created by venkataramana on 29/01/19.
import unittest
from unittest import TestCase
from transformers.executors import ReadFromFile
from transformers.transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager, \
    OutputBender, JsonBenderConfParser


class JsonBenderConfParserTest(TestCase):

    maxDiff = None

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

#
if __name__ == '__main__':
    unittest.main()

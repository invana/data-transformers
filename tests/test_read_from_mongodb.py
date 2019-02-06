# Created by venkataramana on 29/01/19.
import unittest
from unittest import TestCase
import json

from transformers.executors import ReadFromMongo
from transformers.transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager


class ReadFromMongoTest(TestCase):
    maxDiff = None

    def testSample(self):
        mongo_executor = ReadFromMongo('mongodb://127.0.0.1:27017/crawler_data', 'crawler_data', 'website_data')
        mongo_executor.connect()
        ops = [OTConf('items.url', UrlDomainTransformer), OTConf('items.item_no', FloatTransform),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})')]
        results = OTManager(ops).process(mongo_executor).results
        with open('samples/tests_results_expected/sample2.json') as fp:
            expected = json.load(fp)
            fp.close()
        mongo_executor.disconnect()
        self.assertListEqual(results, expected)


if __name__ == '__main__':
    unittest.main()

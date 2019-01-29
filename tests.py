# Created by venkataramana on 29/01/19.
from executors import ReadFromFile, ReadFromMongo
from transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager


class ReadFromFileTest:
    def __init__(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer), OTConf('items.item_no', FloatTransform),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})')]
        OTManager(ops).process(file_executor).print()


class ReadFromMongoTest:
    def __init__(self):
        mongo_executor = ReadFromMongo('mongodb://10.1.0.83:27017/crawler_data', 'crawler_data', 'website_data')
        mongo_executor.connect()
        ops = [OTConf('items.url', UrlDomainTransformer), OTConf('items.item_no', FloatTransform),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})')]
        OTManager(ops).process(mongo_executor).print()
        mongo_executor.disconnect()


ReadFromFileTest()

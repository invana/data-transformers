# Created by venkataramana on 29/01/19.
import json

from jsonbender import S, Context
from jsonbender.list_ops import ForallBend

from executors import ReadFromFile, ReadFromMongo, WriteToFile
from transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager, OutputRenderer, \
    OutputBender, JsonBenderConfParser


class ReadFromFileTest:
    def __init__(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        OTManager(ops).process(file_executor).print()


class ReadFromMongoTest:
    def __init__(self):
        mongo_executor = ReadFromMongo('mongodb://10.1.0.83:27017/crawler_data', 'crawler_data', 'website_data')
        mongo_executor.connect()
        ops = [OTConf('items.url', UrlDomainTransformer), OTConf('items.item_no', FloatTransform),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})')]
        OTManager(ops).process(mongo_executor).print()
        mongo_executor.disconnect()


class OutputRendererTest:
    def __init__(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        ot_manager = OTManager(ops).process(file_executor)
        print(json.dumps(OutputRenderer(
            include=['client_info', 'items.url', 'items.title', 'items.description', 'items.item_no']).expand(
            ot_manager.results), indent=4))


class OutputBenderTest:
    def __init__(self):
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
        print(json.dumps(results, indent=4))
        file_writer = WriteToFile()
        file_writer.write(results, 'crawl_data_2.json')


class JsonBenderConfParserTest:
    def __init__(self):
        file_executor = ReadFromFile('samples/crawler_data.json')
        ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
               OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
               OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
                      update_key='keywords')]
        ot_manager = OTManager(ops).process(file_executor)
        MAPPING = JsonBenderConfParser('samples/confs/bender_conf.json').parse()
        print(MAPPING)
        results = OutputBender(include=MAPPING).expand(ot_manager.results)
        print(json.dumps(results, indent=4))
        file_writer = WriteToFile()
        file_writer.write(results, 'crawl_data_2.json')


JsonBenderConfParserTest()

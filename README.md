# Data Transformers


A library to transforming JSON with parsers.


## install

```bash

pip install git+https://github.com/invanalabs/data-transformers#egg=transformers


``` 


## Usage

```python


from transformers.executors import ReadFromFile
from transformers.transforms import UrlDomainTransformer, OTConf, FloatTransform, RegexTransform, OTManager
import json

file_executor = ReadFromFile('samples/crawler_data.json')
ops = [OTConf('items.url', UrlDomainTransformer, update_element=True, update_key="domain"),
       OTConf('items.item_no', FloatTransform, update_element=True, update_key='item_no_float'),
       OTConf('items.description', RegexTransform, regex='(\w{5,100})', update_element=True,
              update_key='keywords')]
result = OTManager(ops).process(file_executor).results
with open('samples/tests_results_expected/sample1.json') as fp:
    expected = json.load(fp)
    fp.close()


```
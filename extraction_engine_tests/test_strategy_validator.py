import pathlib

import pytest
import yaml

from nn_project.nn_lc.env import DATA_PATH
from extraction_engine.strategy_validator import validate, print_message
from nn_project.nn_lc.pipeline.gateway import api
import logging



def test_validate():
    validate(api, """
document_type:
- 1
- 2
a: aaa
pre:
  resources:
    - ports
    - countries
    - currencies
fields:
  - field_code: F_MT700_Pre_Flatten
    root:
      pipeline: flatten
      params:
        action: documents_to_flatten
        inputs:
          context: document.docs
        outputs:
          X: intermediate.flatten
  - field_code: F_MT700_Pre_Flatten
    root:
      type: xxx
      params:
        action: documents_to_flatten
        inputs:
          context: document.docs
        outputs:
          X: intermediate.flatten
    """)
    pass


def test_validate_should_return_ok():
    total = 0
    logging.info('\n'*2)
    for item in pathlib.Path(DATA_PATH, 'documents').glob('**/*.yaml'):
        with item.open() as f:
            li = list(validate(api, f.read()))
            for ite in li:
                print_message(ite, file_path=item.as_posix())
                total += 1

    if total > 0:
        pytest.fail('Some strategies failed in the validity check')


def test_list_fields_supported():
    total = 0

    def gen():
        for item in pathlib.Path(DATA_PATH, 'documents').glob('**/*.yaml'):
            with item.open() as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
                for item in doc['fields']:
                    yield item['field_code']

    li = list(gen())

    for item in li:
        logging.info(item)

    logging.info('total: {}'.format(len(li)))
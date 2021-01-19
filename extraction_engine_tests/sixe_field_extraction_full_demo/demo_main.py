import json
import logging
import pathlib

from extraction_engine_tests.sixe_field_extraction_full_demo.demo_field_extraction_full_pipeline import extract

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    with pathlib.Path(__file__).with_name('request.json').open('r') as f:
        req = json.load(f)
    result = extract(req)

    logging.info(result)
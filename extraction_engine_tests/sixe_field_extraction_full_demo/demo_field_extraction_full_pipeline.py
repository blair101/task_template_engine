import logging
import pathlib
from typing import List, Dict

import pydash
from ruamel.yaml import YAML

import extraction_engine_tests.sixe_field_extraction_full_demo.demo_regex_pipeline
import extraction_engine_tests.sixe_field_extraction_full_demo.demo_math_pipeline

from extraction_engine import AbstractContext
from extraction_engine.extraction_strategy.strategy_definition import SDRoot, SDNode, SDLeafNode
from extraction_engine.strategy_intepreter.strategy_intepreter import StrategyInterpreter
from extraction_engine_tests.sixe_field_extraction_full_demo.demo_gateway import api


class StrategyLoader:
    def load(self) -> List[SDRoot]:
        path = pathlib.Path(__file__).with_name('INVOICE.yaml')

        yaml = YAML()
        with path.open() as f:
            raw_strategies = yaml.load(f)

        fields = raw_strategies.get('fields')
        strategies = pydash.map_(fields, lambda x: self.build_strategy_root(x, path))
        return strategies

    def build_strategy_root(self, x, path) -> SDRoot:
        sd_root = SDRoot()
        sd_root.field_code = x.get('field_code')
        sd_root.root = self.build_strategy(x.get('root'), path)
        sd_root.raw = x
        sd_root.path = path

        return sd_root

    def build_strategy(self, x, path) -> SDNode:
        pipeline = x.get('pipeline')
        if pipeline is None:
            typ = x.get('type')
            if typ == 'ifelse':
                raw_children = [x.get('condition'), x.get('then'), x.get('else')]
            elif typ in ['all', 'any', 'chain']:
                raw_children = x.get('children')
            else:
                raise Exception(f'Unkown type: {typ}')

            children = pydash.map_(raw_children, lambda xi: self.build_strategy(xi, path))
            sd = SDNode()
            sd.type = x.get('type')
            sd.children = children
            sd.name = x.get('name')
            sd.raw = x
            sd.path = path
            return sd
        else:
            sd = SDLeafNode()
            sd.pipeline = x.get('pipeline')
            sd.params = x.get('params')
            sd.name = x.get('name')
            sd.raw = x
            sd.path = path
            return sd

class Context(AbstractContext):
    def __init__(self, raw: Dict = None):
        self._raw = raw

    def get(self, path, default=None):
        return pydash.get(self._raw, path, default)

    def to_dict(self):
        return self._raw

    def create_copy(self):
        return Context(raw=pydash.clone_deep(self._raw))


def extract(raw_document):
    strategy_fields = StrategyLoader().load()

    context = Context(raw={
        "document": raw_document
    })

    strategies = StrategyInterpreter(api).compile_strategies(strategy_fields)

    for item in strategies:
        context = item.transform(context)

    fields = context.to_dict()['fields']
    return fields
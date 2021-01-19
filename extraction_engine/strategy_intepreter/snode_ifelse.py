import warnings
from typing import List

from extraction_engine import AbstractContext as Context
from extraction_engine.extraction_strategy.strategy_definition import SDNode
from extraction_engine.extraction_strategy.strategy_item import SNode
from extraction_engine.strategy_intepreter.backtrace import nt


class SNodeIfElse(SNode):

    @nt.trace()
    def transform(self, context: Context) -> Context:
        c = self.children[0].transform(context)
        if c.get('state.status'):
            a = self.children[1].transform(context)
            return a
        else:
            b = self.children[2].transform(context)
            return b

    def __init__(self, children: List[SNode], name=None, definition: SDNode = None):
        if len(children) < 3:
            warnings.warn("Invalid parameters for SNodeIfElse: children should be greater than or equal to 3", category=UserWarning)
        self.children = children
        self.name = name
        self.definition = definition

    @property
    def node_name(self):
        if self.name:
            return f'ifelse#{self.name}'
        else:
            return 'ifelse'
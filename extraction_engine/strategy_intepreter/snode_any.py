import warnings
from typing import List

from extraction_engine import AbstractContext as Context
from extraction_engine.extraction_strategy.strategy_definition import SDNode
from extraction_engine.extraction_strategy.strategy_item import SNode
from extraction_engine.strategy_intepreter.backtrace import nt


class SNodeAny(SNode):

    @nt.trace()
    def transform(self, context: Context) -> Context:

        last = None
        for item in self.children:
            copy = context.create_copy()
            o = item.transform(copy)
            last = o
            if o.get('state.status'):
                return o
            else:
                continue

        return last

    def __init__(self, children: List[SNode], name=None, definition: SDNode = None):
        # if len(children) < 2:
        #     warnings.warn("Invalid parameters for SNodeAny: children should be greater than or equal to 2", category=UserWarning)
        self.children = children
        self.name = name
        self.definition = definition

    @property
    def node_name(self):
        return 'any'

import warnings
from typing import List

from extraction_engine import AbstractContext as Context
from extraction_engine.extraction_strategy.strategy_definition import SDNode
from extraction_engine.extraction_strategy.strategy_item import SNode
from extraction_engine.strategy_intepreter.backtrace import nt


class SNodeAll(SNode):

    @nt.trace()
    def transform(self, context: Context) -> Context:

        best_confidence = -1
        best_context = None

        for item in self.children:
            copy = context.create_copy()
            new_context = item.transform(copy)

            confidence_key = 'field.extraction_confidence'
            if new_context.get('state.status') and new_context.get(confidence_key) > best_confidence:
                best_confidence = new_context.get(confidence_key)
                best_context = new_context
            else:
                pass

        if best_context is not None:
            return best_context
        else:
            return new_context

    def __init__(self, children: List[SNode], name=None, definition: SDNode = None):
        # if len(children) < 2:
        #     warnings.warn("Invalid parameters for SNodeAll: children should be greater than or equal to 2", category=UserWarning)
        self.children = children
        self.name = name
        self.definition = definition

    @property
    def node_name(self):
        return 'all'

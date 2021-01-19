import logging
import warnings
from typing import List

from extraction_engine.extraction_strategy.strategy_definition import SDNode
from extraction_engine.extraction_strategy.strategy_item import SNode
from extraction_engine.strategy_intepreter.backtrace import nt

logger = logging.getLogger(__name__)


class SNodeChain(SNode):
    def __init__(self, children: List[SNode], name=None, definition: SDNode = None):
        # if len(children) < 2:
        #     warnings.warn("Invalid parameters for SNodeChain: children should be greater than or equal to 2", category=UserWarning)
        self.children = children
        self.name = name
        self.definition = definition

    @nt.trace()
    def transform(self, context):
        logger.debug(f'{nt.to_path()} invoked')
        for index, child in enumerate(self.children):
            with nt.open_index(index):
                context = child.transform(context)
                status = context.get('state.status')
                if status is not None:
                    logger.debug(f'{nt.to_path()} status code:{status} returned')
                    if status:
                        pass
                    else:
                        return context

        return context

    @property
    def node_name(self):
        if self.name:
            return f'chain#{self.name}'
        else:
            return 'chain'


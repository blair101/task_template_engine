import logging

import pydash

from extraction_engine import AbstractContext as Context
from extraction_engine.extraction_strategy.strategy_definition import SDNode

from extraction_engine.extraction_strategy.strategy_item import SNode
from extraction_engine.strategy_decorator import Api
from extraction_engine.strategy_intepreter.backtrace import nt

logger = logging.getLogger(__name__)


class SNodeLeaf(SNode):

    @nt.trace()
    def transform(self, context: Context) -> Context:
        path = nt.to_path()
        logger.debug(f'{path} invoked')

        #found = re.search(r'INV\.yaml:11$', nt.to_file_line()) is not None
        #conditional break point here, set variable found as the condition variable

        # serialize
        context_dict = context.to_dict()

        p = self.params

        if pydash.get(p, 'mock') is not None:
            state = pydash.get(p, 'mock.state')
            field = pydash.get(p, 'mock.field')
            if state is not None:
                context_dict['state'] = state
            if field is not None:
                context_dict['field'] = field
        else:
            context_dict = self.api.invoke(self.pipeline, self.params['action'], context_dict, self.params)
            # context_dict = context
        # deserialize
        return context.__class__(raw=context_dict)
        # return Context(raw=context_dict)

    def __init__(self, api: Api, pipeline: str, params: dict, name: str = None, definition: SDNode = None):
        self.pipeline = pipeline
        self.params = params
        self.name = name
        self.definition = definition
        self.api = api

    @property
    def node_name(self):
        if self.name:
            return f'{self.pipeline}.{self.params["action"]}#{self.name}'
        else:
            return f'{self.pipeline}.{self.params["action"]}'


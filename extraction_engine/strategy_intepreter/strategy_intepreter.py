from typing import List

import pydash

from extraction_engine.extraction_strategy.field_strategy import FieldStrategy
from extraction_engine.extraction_strategy.strategy_definition import SDRoot, SDNode, SDLeafNode
from extraction_engine.extraction_strategy.strategy_item import SNode
from extraction_engine.strategy_decorator import Api
from extraction_engine.strategy_intepreter.snode_all import SNodeAll
from extraction_engine.strategy_intepreter.snode_chain import SNodeChain
from extraction_engine.strategy_intepreter.snode_ifelse import SNodeIfElse
from extraction_engine.strategy_intepreter.snode_leaves import SNodeLeaf
from extraction_engine.strategy_intepreter.snode_any import SNodeAny


class StrategyInterpreter:

    def __init__(self, api: Api):
        self.api = api

    def compile_strategy(self, strategy_definition: SDNode) -> SNode:
        if isinstance(strategy_definition, SDLeafNode):
            return SNodeLeaf(self.api, strategy_definition.pipeline, strategy_definition.params, name=strategy_definition.name, definition=strategy_definition)
        elif strategy_definition.type == 'chain':
            children = pydash.map_(strategy_definition.children, lambda x: self.compile_strategy(x))
            return SNodeChain(children, name=strategy_definition.name, definition=strategy_definition)
        elif strategy_definition.type == 'any':
            children = pydash.map_(strategy_definition.children, lambda x: self.compile_strategy(x))
            return SNodeAny(children, name=strategy_definition.name, definition=strategy_definition)
        elif strategy_definition.type == 'all':
            children = pydash.map_(strategy_definition.children, lambda x: self.compile_strategy(x))
            return SNodeAll(children, name=strategy_definition.name, definition=strategy_definition)
        elif strategy_definition.type == 'ifelse':
            children = pydash.map_(strategy_definition.children, lambda x: self.compile_strategy(x))
            return SNodeIfElse(children, name=strategy_definition.name, definition=strategy_definition)
        else:
            raise NotImplementedError()

    def compile_strategies(self, strategies: List[SDRoot]) -> List[FieldStrategy]:
        return list(FieldStrategy(root=self.compile_strategy(x.root), field_code=x.field_code) for x in strategies)

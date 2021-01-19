import abc

from extraction_engine import AbstractContext as Context
from extraction_engine.extraction_strategy.strategy_definition import SDNode


class SNode:
    @abc.abstractmethod
    def transform(self, context: Context) -> Context:
        raise NotImplementedError()

    @property
    def node_name(self):
        raise NotImplementedError()

    definition: SDNode

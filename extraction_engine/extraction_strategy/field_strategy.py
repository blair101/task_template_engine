from extraction_engine import AbstractContext as Context
from extraction_engine.extraction_strategy.strategy_item import SNode


class FieldStrategy:
    root: SNode

    def __init__(self, root: SNode, field_code):
        self.root = root
        self.field_code = field_code

    def transform(self, context: Context) -> Context:
        result = self.root.transform(context)
        # print(nt.to_path())
        return result

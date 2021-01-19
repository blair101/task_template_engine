import logging
from contextlib import contextmanager
from typing import List

from extraction_engine.extraction_strategy.strategy_item import SNode

logger = logging.getLogger(__name__)


class NodeTrace:
    stack: List[SNode] = []
    node_stack: List[SNode] = []

    @contextmanager
    def open_node(self, node: SNode):
        self.stack.append(node)
        self.node_stack.append(node)
        try:
            logger.debug(f'{node.definition.path}:{node.definition.raw.lc.line+1} {self.to_path()}')
            yield
        finally:
            self.node_stack.pop()
            self.stack.pop()

    @contextmanager
    def open_index(self, index: int):
        self.stack.append(index)
        try:
            yield
        finally:
            self.stack.pop()

    def to_file_line(self):
        top_node = self.node_stack[-1] if len(self.node_stack) > 0 else None
        if top_node:
            return f'{top_node.definition.path}:{top_node.definition.raw.lc.line+1}'
        else:
            return None

    def to_path(self):

        def to_str(x):
            if isinstance(x, int):
                return str(x)
            elif isinstance(x, SNode):
                return x.node_name
            else:
                raise Exception('Unknown type')

        path = ' > '.join([to_str(x) for x in self.stack])
        return path

    def trace(self):
        def wrapper(func):
            def updated_func(sel, *argv, **kargs):
                with self.open_node(sel):
                    res = func(sel, *argv, **kargs)

                return res

            return updated_func

        return wrapper


nt = NodeTrace()
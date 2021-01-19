from typing import Any, List

from ruamel.yaml.comments import CommentedBase


class SDNode:
    type: str  # FLOW_CONTROL | LEAF
    children: List['SDNode']
    name: str
    raw: CommentedBase


class SDLeafNode(SDNode):
    type = 'LEAF'
    children = None
    pipeline: str
    params: Any


class SDRoot:
    field_code: str
    root: SDNode
    raw: CommentedBase


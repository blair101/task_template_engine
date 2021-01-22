# -*- coding: utf-8 -*-
import re
from ruamel.yaml.comments import CommentedSeq


class Raw(object):
    type_name = "raw"

    def __init__(self, default=None, description=None, reference=None, required=None, example=None, **kwargs):
        self.default = default
        self.description = description
        self.reference = self.generate_schema_reference(reference)
        self.required = required
        # used to generate yaml sample
        self.example = self.generate_flow_style_seq(example) if isinstance(example, list) else example

    def is_valid_value(self, value):
        return True

    def generate_schema_reference(self, value):
        if value:
            re_m = re.search(r'^#([a-zA-z\_\d]+)', value)
            if re_m:
                value = f'[{re_m.group(1)}](../schema.md{value})'
        return value

    def generate_flow_style_seq(self, value):
        value = CommentedSeq(value)
        value.fa.set_flow_style()
        return value


class String(Raw):
    type_name = "string"

    def __init__(self, *args, **kwargs):
        super(String, self).__init__(*args, **kwargs)

    def is_valid_value(self, value):
        return isinstance(value, str)


class Integer(Raw):
    type_name = "integer"

    def __init__(self, *args, **kwargs):
        super(Integer, self).__init__(*args, **kwargs)

    def is_valid_value(self, value):
        return isinstance(value, int)


class Float(Raw):
    type_name = "float"

    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)

    def is_valid_value(self, value):
        return isinstance(value, float)


class Regex(Raw):
    type_name = "regex"

    def __init__(self, *args, **kwargs):
        super(Regex, self).__init__(*args, **kwargs)

    def is_valid_value(self, value):
        if isinstance(value, str):
            import re
            try:
                re.compile(value)
                return True
            except re.error:
                return False


class Boolean(Raw):
    type_name = "boolean"

    def __init__(self, *args, **kwargs):
        super(Boolean, self).__init__(*args, **kwargs)

    def is_valid_value(self, value):
        return isinstance(value, bool)


class Structured(Raw):
    type_name = "structured"

    def __init__(self, schema='', *args, **kwargs):
        super(Structured, self).__init__(*args, **kwargs)
        self.schema = schema

    def is_valid_value(self, value):
        # todo implement json schema validation
        return isinstance(value, object)


class List(Raw):
    type_name = "list"

    def __init__(self, schema='', *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.schema = schema

    def is_valid_value(self, value):
        # todo implement json schema validation
        return isinstance(value, list)

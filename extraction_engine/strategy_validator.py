import re

import pydash

from extraction_engine.strategy_decorator import Api
from extraction_engine.strategy_decorator.fields import Raw

flow_control_rules = [
    {"type": "chain", "fields": ["children"], "fields_type": {
        "children": list
    }},
    {"type": "ifelse", "fields": ["condition", "then", "else"], "fields_type": {
        "condition": dict,
        "then": dict,
        "else": dict,
    }},
    {"type": "any", "fields": ["children"], "fields_type": {
        "children": list
    }}
]
import logging
logger = logging.getLogger(__name__)

from ruamel.yaml import ruamel, sys

yaml = ruamel.yaml.YAML()

FIELD_NOT_ALLOWED = 'FIELD_NOT_ALLOWED'
FIELD_WRITE_NOT_ALLOWED = 'FIELD_WRITE_NOT_ALLOWED'
FIELD_MISSING = 'FIELD_MISSING'
DEFINITE_ACTION_MISSING = 'DEFINITE_ACTION_MISSING'
DEFINITE_ACTION_BANNED = 'DEFINITE_ACTION_BANNED'
ERROR = 'ERROR'
WARNING = 'WARNING'


class ValidationMessage:
    def __init__(self, code, message=None, lc=None, level='ERROR'):
        self.code = code
        self.message = message
        self.lc = lc
        self.level = level


def allow_fields(yml, fields):
    """
    if any fields in the yml file is not in feilds, yield an error message
    """
    if yml is None:
        return

    fs = set(fields)

    for field in yml.keys():
        if field in fs:
            pass
        else:
            lc = yml.lc.data[field]
            yield ValidationMessage(code=FIELD_NOT_ALLOWED,
                                    message=f"field '{field}' is not allowed here",
                                    level=ERROR,
                                    lc=lc)


def allow_value(yml, field, values):
    """
    if value of field in yml is not one of values, yield an error message
    """
    fs = set(values)
    if yml[field] not in fs:
        lc = yml.lc.data[field]
        yield ValidationMessage(code=FIELD_NOT_ALLOWED,
                                message=f"field value '{yml[field]}' is not allowed here",
                                level=ERROR,
                                lc=lc)


def require_fields(yml, fields):
    """
    if any one of fields is not in yml, yield an error
    """
    for field in fields:
        if field in yml:
            pass
        else:
            line = yml.lc.line
            col = yml.lc.col
            yield ValidationMessage(code=FIELD_MISSING,
                                    message=f"field '{field}' is missing here",
                                    level=ERROR,
                                    lc=[line, col, None, None])


def allow_outputs(yml, action_definition):
    """
    if any value in yml does not match pattern, yield an error message
    """
    if yml is None:
        return

    if action_definition.definite:
        allowed_paths = ['state', 'intermediate', 'field']
    else:
        allowed_paths = ['state', 'intermediate']

    pattern = re.compile(r'^({})'.format('|'.join(allowed_paths)))

    for key, value in yml.items():
        if pattern.match(value):
            pass
        else:
            lc = yml.lc.data[key]
            yield ValidationMessage(code=FIELD_WRITE_NOT_ALLOWED, message=f"write operation to '{value}' is not allowed", lc=lc)


def ban_definite_leaf(api, yml):
    """
    if type is any or chain, check its children. otherwise if action is difinite, yield error message
    """
    if 'type' in yml:
        typ = yml['type']
        if typ == 'any' or typ == 'chain':
            for child in pydash.get(yml, 'children'):
                yield from ban_definite_leaf(api, child)
        else:
            raise NotImplementedError()
    elif 'pipeline' in yml:
        pipeline = yml['pipeline']
        action = pydash.get(yml, ['params', 'action'])

        if api.namespace_by_name.get(pipeline) is None or api.namespace_by_name[pipeline].action_by_name.get(action) is None:
            return

        if api.namespace_by_name[pipeline].action_by_name[action].definite:
            lc = yml.lc.data['pipeline']
            yield ValidationMessage(code=DEFINITE_ACTION_BANNED,
                                    message=f"Definite action is not allowed here", lc=lc)
        else:
            pass


def require_definite_leaf(api, yml):
    """
    if type is any, require definite leaf
    if type is chain, the last child must be definite and all other child must be not
    """
    if 'type' in yml:
        typ = yml['type']
        if typ == 'any':
            for child in pydash.get(yml, 'children'):
                yield from require_definite_leaf(api, child)
        elif typ == 'chain':
            last_child = pydash.get(yml, ['children', -1])
            yield from require_definite_leaf(api, last_child)
            children = pydash.get(yml, ['children'])
            for child in children[:-1]: #other children
                yield from ban_definite_leaf(api, child)
        else:
            raise NotImplementedError()
    elif 'pipeline' in yml:
        pipeline = yml['pipeline']
        action = pydash.get(yml, ['params', 'action'])

        if pydash.get(api.namespace_by_name, [pipeline, 'action_by_name', action]) is None:
            return

        if api.namespace_by_name[pipeline].action_by_name[action].definite:
            pass
        else:
            lc = yml.lc.data['pipeline']
            yield ValidationMessage(code=DEFINITE_ACTION_MISSING, message=f"Definite action is missing after this action", lc=lc)



def require_type(yml, fields):
    """
    item must have type typ in yml
    """
    for (item, typ) in fields:
        if item in yml and not isinstance(yml[item], typ):
            lc = yml.lc.data[item]
            yield ValidationMessage(code='INVALID_TYPE', message=f"'{item}' should be of type: {typ.__name__}", lc=lc)


flow_control_rules_by_type = pydash.chain(flow_control_rules).group_by('type').map_values('[0]').value()


def check_pipeline_params(params, definition):
    """
    check definition values are valid
    """
    for key, val in params.items():
        if key not in ['action', 'inputs', 'outputs']:
            defni = pydash.get(definition, ['params', key])
            if isinstance(defni, Raw):
                if defni.is_valid_value(val):
                    pass
                else:
                    lc = params.lc.data[key]
                    yield ValidationMessage(code='INVALID_PARAMETER_TYPE', message=f"'{key}' is invalid", lc=lc)
    pass


def validate_strategy(api, yml):
    if 'type' in yml:
        typ = yml['type']
        # type must be in flow_control_rules_by_type keys()
        yield from allow_value(yml, 'type', flow_control_rules_by_type.keys())
        fields = pydash.get(flow_control_rules_by_type, [typ, 'fields'], [])
        types = pydash.get(flow_control_rules_by_type, [typ, 'fields_type'], dict()).items()
        # all fields in yml must be in fields + ['type', 'name']
        yield from allow_fields(yml, fields + ['type', 'name'])
        # all fields must be in yml
        yield from require_fields(yml, fields)
        # all fileds type must match that in types
        yield from require_type(yml, types)

        # validate child, if child == 'children' then validate each one of them
        for child in pydash.get(flow_control_rules_by_type, [typ, 'fields'], []):
            if child == 'children':  # todo to generalize this
                for ite in pydash.get(yml, child):
                    yield from validate_strategy(api, ite)
            else:
                yield from validate_strategy(api, pydash.get(yml, [child]))

    elif 'pipeline' in yml:
        yield from require_fields(yml, ['pipeline', 'params'])
        yield from allow_fields(yml, ['pipeline', 'params', 'name'])
        pipeline = yml['pipeline']
        action = pydash.get(yml, ['params', 'action'])
        params = yml.get('params')
        if params is None:
            return


        # pipeline fields must have value as in api.namespace_by_name.keys()
        yield from allow_value(yml, 'pipeline', api.namespace_by_name.keys())

        if api.namespace_by_name.get(yml.get('pipeline')) is None:
            return

        yield from allow_value(pydash.get(yml, 'params'), 'action',
                               api.namespace_by_name[pipeline].action_by_name.keys())

        if pydash.get(yml, ['params', 'action']) not in api.namespace_by_name[pipeline].action_by_name.keys():
            return

        ns = pydash.get(api.namespace_by_name, [pipeline])

        action_definition = pydash.get(ns.action_by_name, action)

        if action_definition is None:
            return

        expects_inputs = pydash.get(api.namespace_by_name, [pipeline, 'expects', action_definition.func, 'inputs']) or {}
        expects_outputs = pydash.get(api.namespace_by_name, [pipeline, 'expects', action_definition.func, 'outputs']) or {}
        expects_params = pydash.get(api.namespace_by_name, [pipeline, 'expects', action_definition.func, 'params']) or {}

        def filter_required_fields(x):
            return pydash.filter_(x.keys(), lambda xi: x[xi].required)

        expect_inputs_required = filter_required_fields(expects_inputs)
        expect_outputs_required = filter_required_fields(expects_outputs)
        # check required inputs per expects
        if len(expect_inputs_required) > 0:
            if params.get('inputs'):
                yield from require_fields(params.get('inputs'), expect_inputs_required)
            else:
                yield from require_fields(params, ['inputs'])

        # check required outputs
        if len(expect_outputs_required) > 0:
            if params.get('outputs'):
                yield from require_fields(params.get('outputs'), expect_outputs_required)
            else:
                yield from require_fields(params, ['outputs'])

        yield from require_fields(params, filter_required_fields(expects_params))

        yield from allow_fields(params.get('inputs'), expects_inputs.keys())
        yield from allow_fields(params.get('outputs'), expects_outputs.keys())
        yield from allow_fields(params, list(expects_params.keys()) + ['inputs', 'outputs', 'action'])
        yield from allow_outputs(params.get('outputs'), action_definition)

        yield from check_pipeline_params(params,  pydash.get(api.namespace_by_name, [pipeline, 'expects', action_definition.func]))


def validate_fields(api, yml):
    for item in yml:
        yield from allow_fields(item, ['field_code', 'root', 'skip_definite_action_check'])
        yield from require_fields(item, ['field_code', 'root'])
        yield from require_type(item, [('field_code', str), ('root', dict)])
        yield from validate_strategy(api, item['root'])
        if pydash.get(item, 'skip_definite_action_check'):
            pass
        else:
            yield from require_definite_leaf(api, item['root'])


def validate_document(api, yml):
    yield from allow_fields(yml, ['document_type', 'pre', 'fields'])
    yield from require_fields(yml, ['document_type', 'fields'])
    yield from require_type(yml, [('document_type', str), ('fields', list)])

    yield from validate_fields(api, yml['fields'])
    # print(api)


def validate(api: Api, template_plain_text):
    yml = yaml.load(template_plain_text)
    # raise Exception('wer')
    yield from validate_document(api, yml)


def print_message(msg: ValidationMessage, file_path, fp=sys.stdout):
    logger.info(f'{file_path}:{msg.lc[0] + 1} [{msg.level}] {msg.code} {msg.message}')

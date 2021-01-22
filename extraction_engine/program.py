import pydash
from typing import Dict

from extraction_engine.strategy_decorator import Namespace, Action
import re
from jsonschema import validate, Draft7Validator
import json
import pathlib
from collections import defaultdict
from .validators import ProgramValidator

import logging

logger = logging.getLogger(__name__)


def _build_strategy_tpl_index(tpls, group_by):
    groups = defaultdict(list)
    grouped = defaultdict(dict)
    base_fields = defaultdict(list)
    for it in tpls:
        group = tuple(it['labels'][k] for k in group_by)
        for ite in it['document']['fields']:
            grouped[group][ite['field_code']] = ite
            groups[group].append(ite['field_code'])

        for ite in pydash.get(it, ['document', 'pre', 'base_fields']) or []:
            base_fields[group].append(ite)

    return grouped, groups, base_fields


class Program:
    def __init__(self, strategy_templates_loader, action_loader, resource_loader, group_by):
        self.validator = ProgramValidator()

        strategy_templates = list(strategy_templates_loader())
        apis = list(action_loader())

        self.validator.validate_program_strategy_and_actions(
            strategy_templates,
            [ns for api in apis for ns in api.namespaces],
            group_by)

        # _validate_strategy_templates(strategy_templates)
        self.field_by_group_code, self.groups, self.base_fields = _build_strategy_tpl_index(strategy_templates,
                                                                                            group_by)
        self.strategy_templates = strategy_templates

        self.actions_by_ns = {
            ns.name: ns for api in apis for ns in api.namespaces
        }

        self.resource_loader = resource_loader
        # _validate_program_strategy_and_actions(
        #     [ns  for api in apis for ns in api.namespaces], 
        #     strategy_templates, group_by)

        self.group_key_index = {
            it: idx for idx, it in enumerate(group_by)
        }

    def run(self, fields, document, groups):
        resources = self.resource_loader()

        values = []

        failed_fields = []

        for group in groups:
            visited = set()
            sequence = []
            base_fields = self.base_fields[group]
            for code in base_fields:
                sequence.append(code)
                visited.add(code)

            for field in fields:
                for code in self._visit(visited, group, field):
                    sequence.append(code)

            intermediate = {}

            failed = set()

            for idx, field_code in enumerate(sequence):
                dependency_failed = False
                requires = self.field_by_group_code[group][field_code].get('requires') or []
                for it in [*requires, *base_fields]:
                    if it in failed:
                        dependency_failed = True
                        break

                if dependency_failed:
                    failed.add(field_code)
                    failed_fields.append({
                        "field_code": field_code,
                        "group": group,
                        "cause": "DEPENDENCY_FAILED"
                    })
                    continue

                context = {
                    "state": {},
                    "intermediate": intermediate,
                    "field": {},
                    "document": pydash.clone_deep(document),
                    "resources": resources
                }

                ctx, success = self._evaluate_field_strategy(group, field_code, context)

                if success:
                    intermediate = ctx['intermediate']
                    values.append({
                        "field_code": field_code,
                        "values": pydash.get(ctx, ['field']),
                        "group": group
                    })
                else:
                    failed.add(field_code)
                    failed_fields.append({
                        "field_code": field_code,
                        "group": group,
                        "cause": "STRATEGY_FAILED"
                    })

        return Result(values, failed_fields, [])

    def _evaluate_field_strategy(self, group, field_code, context):
        field = self.field_by_group_code[group][field_code]
        ret = self._transform(field['strategy'], context)
        return ret

    def _transform(self, stragety_node, context):
        action_identifer = pydash.get(stragety_node, ['action'])
        if action_identifer:
            # params = pydash.get(stragety_node, ['params'])
            action_group_name, action = re.split(r'\.', action_identifer)
            ns = self.actions_by_ns[action_group_name]
            pipeline_action = ns.action_by_name[action]
            pipeline_instance = ns.get_pipeline_instance()
            args = _extract_args(ns, pipeline_action, context, stragety_node)
            try:
                pipeline_action.validate_kargs(args)
                rv, success = pipeline_action.func(pipeline_instance, **args)
                pipeline_action.validate_return_values(rv)
            except Exception:
                logger.exception('Failed to perform action: %s', action_identifer)
                return context, False

            return_context = _write_output(context, rv, ns, pipeline_action, stragety_node, success)
            return return_context, success
        else:
            # type_ = pydash.get(stragety_node, ['type'])
            if 'chain' in stragety_node:
                for index, child in enumerate(pydash.get(stragety_node, ['chain'])):
                    context, success = self._transform(child, context)
                    if success:
                        pass
                    else:
                        return context, success

                return context, success

            elif 'any' in stragety_node:
                for index, child in enumerate(pydash.get(stragety_node, ['any'])):
                    copy = pydash.clone_deep(context)
                    copy, success = self._transform(child, copy)
                    if success:
                        return copy, success

                return copy, success
            else:
                raise ValueError(f'Unkonw node type')

    def _visit(self, visited, group, field_code):
        if field_code in visited:
            return

        if pydash.get(self.field_by_group_code, [group, field_code]) is None:
            return

        field = self.field_by_group_code[group][field_code]

        visited.add(field_code)
        assert field is not None, f'field_code: {field_code} not defined in group {group}'
        for item in field.get('depends') or []:
            yield from self._visit(visited, group, item)

        for item in field.get('requires') or []:
            yield from self._visit(visited, group, item)

        yield field_code

    def get_fields_in_group(self, group):
        ret = self.groups[group]
        return ret

    def _group_match(self, group, criteria):
        if not criteria:
            return True

        for k, v in criteria.items():
            if group[self.group_key_index[k]] != v:
                return False

        return True

    def get_all_groups(self, **kargs):
        return list(it for it in self.groups.keys() if self._group_match(it, kargs))

    def get_all_fields(self, **kargs):
        acc = set()
        for group in self.get_all_groups():
            if self._group_match(group, kargs):
                for it in self.get_fields_in_group(group):
                    acc.add(it)

        return list(acc)


def _extract_args(ns: Namespace, action: Action, context: Dict, strategy: Dict):
    if action.kargs_schema:
        return _extract_args_v2(ns, action, context, strategy)
    else:
        return _extract_args_v1(ns, action, context, strategy)


def _extract_args_v2(ns: Namespace, action: Action, context: Dict, strategy: Dict):
    properties = pydash.get(action.kargs_schema, ['properties']) or {}
    default_values = {
        k: pydash.get(v, ['default']) for k, v in properties.items()
    }

    args = {}

    for key in action.input_args or []:
        path = pydash.get(strategy, ['inputs', key])
        if path is None:
            value = default_values.get(key)
        elif path == '.':
            value = context
        else:
            value = pydash.get(context, path)
        pydash.set_(args, key, value)

    for key in action.param_args or []:
        value = pydash.get(strategy, ['params', key], default_values.get(key))
        pydash.set_(args, key, value)

    return args


def _extract_args_v1(ns: Namespace, action: Action, context: Dict, strategy: Dict):
    expects_inputs = pydash.get(ns.expects, [action.func, 'inputs'], dict())
    expects_outputs = pydash.get(ns.expects, [action.func, 'outputs'], dict())
    expects_params = pydash.get(ns.expects, [action.func, 'params'], dict())

    args = {}

    for key, definition in expects_inputs.items():
        path = pydash.get(strategy, ['inputs', key], definition.default)
        if path == '.':
            value = context
        else:
            value = pydash.get(context, path)

        pydash.set_(args, key, value)

    for key, definition in expects_params.items():
        value = pydash.get(strategy, ['params', key], definition.default)
        pydash.set_(args, key, value)

    return args


def _write_output(context, outputs, ns, action, strategy, success):
    if action.kargs_schema:
        return _write_output_v2(context, outputs, ns, action, strategy, success)
    else:
        return _write_output_v1(context, outputs, ns, action, strategy, success)


def _write_output_v2(context, outputs, ns, action: Action, strategy, success):
    properties = pydash.get(action.return_value_schema, ['properties']) or {}

    for key in properties:
        path = pydash.get(strategy, ['outputs', key])
        value = pydash.get(outputs, key)
        pydash.set_(context, path, value)

    return context


def _write_output_v1(context, outputs, ns, action, strategy, success):
    expects_outputs = pydash.get(ns.expects, [action.func, 'outputs'], dict())

    for key, definition in expects_outputs.items():
        path = pydash.get(strategy, ['outputs', key])
        value = pydash.get(outputs, key)
        pydash.set_(context, path, value)

    return context


class Result:
    def __init__(self, values, failed_fields, stats):
        self.values = values
        self.failed_fields = failed_fields
        self.stats = stats

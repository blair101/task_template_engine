import pathlib
import json
from jsonschema import Draft7Validator
import pydash

from ruamel.yaml import YAML
from collections import defaultdict
import re

def visit_strategy_recursively(strategy):
    if 'action' in strategy:
        yield 'action', strategy
    elif 'chain' in strategy:
        yield 'chain', strategy
        for item in strategy['chain']:
            yield from visit_strategy_recursively(item)
    elif 'any' in strategy:
        yield 'any', strategy
        for item in strategy['any']:
            yield from visit_strategy_recursively(item)
    else:
        raise ValueError('Unkonw strategy')

class ProgramValidator:
    def __init__(self):
        schema_path = pathlib.Path(__file__).parent / 'resources/strategy.schema.json'
        with schema_path.open() as f:
            strategy_schema = json.load(f)
        self.strategy_validator = Draft7Validator(strategy_schema)

        schema_path = pathlib.Path(__file__).parent / 'resources/strategy_loading.schema.json'
        with schema_path.open() as f:
            strategy_loading_schema = json.load(f)

        self.strategy_loading_validator = Draft7Validator(strategy_loading_schema)

        self.yaml = YAML()


    def validate_cm(self, validator, document, key=None):
        for error in validator.iter_errors(document):
            key_path = list(error.relative_path)
            if key_path:
                
                with open(key) as f:
                    cm = self.yaml.load(f)

                parent_obj = pydash.get(cm, key_path[:-1])
                line = parent_obj.lc.data[key_path[-1]][0]
                message = f'{key}:{line + 1} {error.message}'
                raise ValueError(message)
                # if logger.isEnabledFor(logging.ERROR):
                #     logger.error()
            else:
                message = f'{key}: {error.message}'
                raise ValueError(message)
                # if logger.isEnabledFor(logging.ERROR):
                #     logger.error(f'{key}: {error.message}')

    def validate(self, validator, document):
        validator.validate(document)

    def validate_program_strategy_and_actions(self, strategy_templates, action_nss, group_by):
        for it in strategy_templates:
            for ite in group_by:
                if pydash.get(it, ['labels', ite]) is None:
                    raise ValueError('Label [{}] for document {} is required but missing'.format(ite, it['key']))

            self.validate(self.strategy_loading_validator, it)
            self.validate_cm(self.strategy_validator, it['document'], key=it['key'])

        duplicates = pydash.duplicates([it.name for it in action_nss])
        if duplicates:
            raise ValueError('Action namespaces {} duplicated'.format(', '.join(duplicates)))

        grouped = defaultdict(dict)

        for it in strategy_templates:
            group_key = tuple([it['labels'][x] for x in group_by])
            for ite in it['document']['fields']:
                code = ite['field_code']
                if code in grouped[group_key]:
                    msg = 'Field: {} duplicates in strategy group: ({})'.format(code, ','.join(group_key))
                    raise ValueError(msg)
                else:
                    grouped[group_key][code] = ite

        for it in strategy_templates:
            group_key = tuple([it['labels'][x] for x in group_by])
            for ite in it['document']['fields']:
                for item in pydash.get(ite, 'depends') or []:
                    if item not in grouped[group_key]:
                        raise ValueError(f"Depended field {item} does not exist in group ({','.join(group_key)})")

            for item in pydash.get(it, ['document', 'pre', 'base_fields']) or []:
                    if item not in grouped[group_key]:
                        raise ValueError(f"Base field {item} does not exist in group ({','.join(group_key)})")

        action_grouped = dict()

        for it in action_nss:
            action_grouped[it.name] = it

        for it in strategy_templates:
            group_key = tuple([it['labels'][x] for x in group_by])
            for ite in it['document']['fields']:
                for typ, item in visit_strategy_recursively(ite['strategy']):
                    if 'action' == typ:
                        ns, action = re.split(r'\.', item['action'])
                        if ns not in action_grouped:
                            raise ValueError(f'Action namespace {ns} does not exist')
                        if action not in action_grouped[ns].action_by_name:
                            raise ValueError(f'Action {action} does not exist in namespace {ns}')
                        

        # duplicates = pydash.duplicates([it.name for it in action_nss])
        # duplicates = pydash.duplicates([it.name for it in action_nss])
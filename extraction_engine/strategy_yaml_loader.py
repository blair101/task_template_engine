import logging
from abc import ABCMeta, abstractmethod
from typing import Callable

import pydash

logger = logging.getLogger(__file__)


class YamlProcessFactory:
    """ The factory class for creating yaml process strategy"""

    registry = {}
    """ Internal registry for available yaml process strategy"""

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: BaseYamlProcess) -> Callable:
            if name in cls.registry:
                logger.warning('Yaml %s already exists. Will replace it',
                               name)
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create_processor(cls, name: str = 'default',
                         **kwargs) -> 'BaseYamlProcess':
        """ Factory command to create the Processor.
        """
        if name not in cls.registry:
            raise ValueError('Processor %s does not exist in the registry')

        exec_class = cls.registry[name]
        processor = exec_class(**kwargs)
        return processor


class BaseYamlProcess(metaclass=ABCMeta):
    @abstractmethod
    def process(self, f):
        pass


@YamlProcessFactory.register('default')
class DefaultYamlProcess(BaseYamlProcess):
    def __init__(self, ):
        """
        default do nothing
        """
        pass

    def process(self, f):
        return f


@YamlProcessFactory.register('model')
class ModelYamlProcess(BaseYamlProcess):
    def __init__(self, ):
        """
        Generatation of Yaml Documents
        """
        pass

    @staticmethod
    def to_flatten_deep(root):
        flatten_dict = {}
        def dfs(o, prefix=''):
            prefix_dot = f'{prefix}.' if prefix != '' else prefix
            if isinstance(o, dict):
                return {
                    key: dfs(value, f'{prefix_dot}{key}') for
                    key, value in o.items()
                }
            elif isinstance(o, list):
                return [dfs(it, f'{prefix_dot}[{i}]') for i, it in enumerate(o)]
            else:
                flatten_dict[prefix] = o
                return o
        dfs(root)
        return flatten_dict

    def process(self, f):
        """
        duplicates field codes in yaml file

        Before

        template: model
        template_params:
            FIELD_CODES: [ 'F_MT700_1','F_MT700_2']
        fields:
          - field_code: +FIELD_CODES
            strategy:
              chain:
                - action: fe_model.convert_and_tokenize
                  inputs:
                    context: document
        After

        template: model
        template_params:
            FIELD_CODES: [ 'F_MT700_1','F_MT700_2']
        fields:
          - field_code: F_MT700_1
            strategy:
              chain:
                - action: fe_model.convert_and_tokenize
                  inputs:
                    context: document
          - field_code: F_MT700_2
            strategy:
              chain:
                - action: fe_model.convert_and_tokenize
                  inputs:
                    context: document

        :param f:
        :return:
        """
        assert 'template_params' in f
        duplicate_keys = f['template_params']
        all_fields = f['fields']
        # get flatten path mapping Eg '[0].field_name'
        flatten_map = self.to_flatten_deep(all_fields)
        # find path with +
        filter_paths = {k: v for k, v in flatten_map.items() if
                        str(v).startswith('+')}
        generated_strategy_templates = []
        marked_as_drop = []
        # loop path
        for path, code in filter_paths.items():
            replace_code_key = code[1:]
            assert replace_code_key in duplicate_keys
            to_replace_lst = duplicate_keys[replace_code_key]

            p1 = path.split('.')[0]
            p2 = '.'.join(path.split('.')[1:])
            # get field to replace
            one_field = pydash.get(all_fields, p1)
            for replace_str in to_replace_lst:
                clone_field = pydash.clone_deep(one_field)
                pydash.set_(clone_field, p2, replace_str)
                generated_strategy_templates.append(clone_field)
            marked_as_drop.append(one_field)
        # cleaning
        all_fields = [field for field in all_fields if
                      field not in marked_as_drop]
        all_fields.extend(generated_strategy_templates)
        f['fields'] = all_fields
        return f

import abc
from typing import Callable, Dict
from jsonschema import Draft7Validator
import pydash
import logging

logger = logging.getLogger(__name__)

class Api:
    def __init__(self, title=None, description=None):
        self.namespaces = []
        self.title = title
        self.description = description

    def namespace(self, name, description=None, path=None, decorators=None, validate=None,
                 authorizations=None, ordered=False, **kwargs):
        '''
        A namespace factory.

        :returns Namespace: a new namespace instance
        '''
        ns = Namespace(name=name, **kwargs)
        self.add_namespace(ns)
        return ns

    def add_namespace(self, ns):
        for item in self.namespaces:
            if item.name == ns.name:
                raise Exception(f"Namespace {ns.name} already exists!")

        self.namespaces.append(ns)

    @property
    def namespace_by_name(self) -> Dict[str, 'Namespace']:
        d = dict((item.name, item) for item in self.namespaces)
        return d

    @abc.abstractmethod
    def invoke(self, *args, **kwargs):
        pass


class Action:
    name: str
    func: Callable
    definite: bool

    def __init__(self, func, name=None, definite=False, kargs_schema=None, return_value_schema=None, input_args=None, param_args=None):
        self.name = name
        self.func = func
        self.definite = definite
        self.kargs_schema = kargs_schema
        self.return_value_schema = return_value_schema
        if kargs_schema:
            self.kargs_schema_validator = Draft7Validator(kargs_schema)
        else:
            self.kargs_schema_validator = None

        if return_value_schema:
            self.return_value_schema_validator = Draft7Validator(return_value_schema)
        else:
            self.return_value_schema_validator = None

        self.input_args = input_args
        self.param_args = param_args
        

    def validate_kargs(self, kargs):
        if self.kargs_schema_validator:
            for it in self.kargs_schema_validator.iter_errors(kargs):
                logger.warning('Action:%s kargs error: %s', self.name, it.message)
    
    def validate_return_values(self, rv):
        if self.return_value_schema_validator:
            for it in self.return_value_schema_validator.iter_errors(rv):
                logger.warning('Action:%s return value error: %s', self.name, it.message)

    

class Namespace(object):
    name: str
    action_entities: Dict[Callable, Action]
    doc_entities: dict

    def __init__(self, name, description=None, path=None, decorators=None, validate=None,
                 authorizations=None, ordered=False, **kwargs):
        self.action_entities = {}
        self.doc_entities = {}
        self.name = name
        self.description = description
        self.path = path
        self.pipeline_class = None
        self.pipeline_instance = None
        self.expects = {}
        self.action_by_name = {}

    def get_pipeline_instance(self):
        if self.pipeline_instance is None:
            self.pipeline_instance = self.pipeline_class()
        return self.pipeline_instance


    def pipeline(self):
        def wrapper(cls):
            self.pipeline_class = cls

            return cls
        return wrapper
    
    def action_ns(self):
        def wrapper(cls):
            self.pipeline_class = cls

            return cls
        return wrapper

    def action(self, name=None, definite=False,
            kargs_schema=None, 
            input_args=None,
            param_args=None,
            return_value_schema=None):
        def wrapper(func):
            action_name = name or func.__name__
            action = Action(func, 
                kargs_schema=kargs_schema, 
                input_args=input_args,
                param_args=param_args,
                return_value_schema=return_value_schema)
            action.name = action_name
            action.definite = definite
            self.action_entities[func] = action
            if action_name in self.action_by_name:
                raise ValueError(f'Action {action_name} already exists in {self.name}')
                
            self.action_by_name[action_name] = action
            return func
        return wrapper

    def doc(self, doc_str):
        def wrapper(func):
            self.doc_entities[func] = doc_str
            return func
        return wrapper

    def expect_inputs(self, model=None):
        def wrapper(func):
            pydash.set_(self.expects, [func, 'inputs'], model or {})
            return func
        return wrapper

    def expect_outputs(self, model=None):
        def wrapper(func):
            pydash.set_(self.expects, [func, 'outputs'], model or {})
            return func
        return wrapper

    def expect_params(self, model=None):
        def wrapper(func):
            pydash.set_(self.expects, [func, 'params'], model or {})
            return func
        return wrapper

    # @property
    # def action_by_name(self):
    #     d = dict((item.name, item) for item in self.action_entities.values())
    #     return d

    def to_dict(self):
        return self.__dict__

    def model(self, *args):
        pass
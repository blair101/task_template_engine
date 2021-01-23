# task_template_engine

## Api (namespaces)

```python
class Api:
    def __init__(self, title=None, description=None):
        self.namespaces = []
        self.title = title
        self.description = description
```

## Namespace (action_group_name)

```python
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
```

## Action

```python
class Action:
    name: str
    func: Callable
    definite: bool
    
def __init__(self, func, name=None, definite=False, kargs_schema=None, return_value_schema=None, input_args=None, param_args=None):
    self.name = name
    self.func = func
    self.definite = definite
    # self.kargs_schema = kargs_schema
    # self.return_value_schema = return_value_schema

    self.input_args = input_args
    self.param_args = param_args
```

## Example

```yaml
document_type: STATS
pre:
  define:
    TERM_CHARS: &TERM_CHARS ((\:|t)\s?\d+[A-Z]?\s?\:)|(^\*\*)|(^F$)   # t is to fix error such as t47A:

  resources:
  - ports
  - countries
  - currencies

  base_fields:
  - pi

fields:
- field_code: pi
  strategy: 
    action: math.pi
    outputs:
      x: intermediate.PI
```

# task_template_engine

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

- field_code: sum
  strategy:
    action: math.sum
    inputs:
      x: document
    outputs:
      x: intermediate.sum

- field_code: len
  strategy:
    action: list.len
    inputs:
      x: document
    outputs:
      x: intermediate.len

- field_code: mean
  requires:
  - sum
  - len
  strategy:
    chain:
    - action: math.divide
      inputs:
        x1: intermediate.sum
        x2: intermediate.len
      outputs:
        x: state.divide
    - action: utils.write_field_value
      inputs:
        x: state.divide
      outputs:
        x: field

- field_code: std
  depends:
    - "mean"
  strategy:
    chain:
    - action: math.std
      inputs: 
        x: document
      outputs:
        x: state.std
    - action: utils.write_field_value
      inputs:
        x: state.std
      outputs:
        x: field
```

# run process

input: 

 1. load_strategy_templates - muilti-yamls
 2. load_actions - multi-api, multi-namespaces[]
 3. load_resources - other

```python
p.run(fields=['mean', 'std'], document=[1, 2, 3, 4], groups=[('rule_based',)])
```


## 2. one-field

```python
context = {
    "state": {},
    "intermediate": intermediate,
    "field": {},
    "document": pydash.clone_deep(document),
    "resources": resources
}
# context 贯穿始终
```

> intermediate, state 维持变量作用域

field

```json
{
  "field_code": "pi",
  "strategy": {
    "action": "math.pi",
    "outputs": {
      "x": "intermediate.PI"
    }
  }
}
```

## 3. core-code

```python
def _evaluate_field_strategy(self, group, field_code, context):
    field = self.field_by_group_code[group][field_code]
    ret = self._transform(field['strategy'], context)
    """
      "strategy": {
        "action": "math.pi",
        "outputs": {
          "x": "intermediate.PI"
        }
      }
    """
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
        # args:{'x': [1,2,3,4]} , action: list.len   
        try:
            pipeline_action.validate_kargs(args)
            rv, success = pipeline_action.func(pipeline_instance, **args)
            pipeline_action.validate_return_values(rv)
        except Exception:
            logger.exception('Failed to perform action: %s', action_identifer)
            return context, False

        return_context = _write_output(context, rv, ns, pipeline_action, stragety_node, success)
        return return_context, success
```

## 4. action 的封装

### Api (namespaces)

```python
class Api:
    def __init__(self, title=None, description=None):
        self.namespaces = []
        self.title = title
        self.description = description
```

### Namespace (action_group_name)

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

### Action

```python
class Action:
    name: str
    func: Callable
    
def __init__(self, func, name=None, definite=False, kargs_schema=None, return_value_schema=None, input_args=None, param_args=None):
    self.name = name
    self.func = func

    self.input_args = input_args
    self.param_args = param_args
```

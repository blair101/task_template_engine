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
    """
    "strategy": {
      "action": "math.pi",
      "outputs": {
        "x": "intermediate.PI"
      }
    }
    """
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


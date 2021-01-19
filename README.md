# task_template_engine

## Api

## Actions

## Namespace

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

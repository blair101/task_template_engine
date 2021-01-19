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
```

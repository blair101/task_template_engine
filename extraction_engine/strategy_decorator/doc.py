import pathlib
import re

import pydash

from extraction_engine.strategy_decorator import Api, Namespace


def indent(txt, cnt=0):
    lines = txt.split('\n')
    lines = pydash.map_(lines, lambda l: ' ' * cnt + l)
    return '\n'.join(lines)


def doc_md(ns: Namespace):

    def trim_python_func_doc(txt):
        txt = re.sub(r'\t', ' ' * 4, txt)
        lines = pydash.lines(txt)
        if len(lines) == 0:
            return ''
        lines = pydash.filter_(lines, lambda x: re.search(r'^\s*\S', x))
        lines = pydash.map_(lines, lambda x: re.search(r'^(\s*)\S', x).group(1))
        cnts = pydash.map_(lines, lambda x: len(x))
        if len(cnts) < 1:
            return ''
        min_cnt = pydash.min_(cnts)
        lines2 = pydash.map_(pydash.lines(txt), lambda x: x[min_cnt:])
        lines2 = pydash.filter_(lines2, lambda x: re.search(r'^\:[^\:]+\:', x) is None)
        return '\n'.join(lines2)

    def gen_param_table(title, definition_dict):
        if len(definition_dict) < 1:
            return
        yield f"- {title}"

        if title == 'Params':
            yield """
| Name | Type | Required | Default | Sample | Description |
|:-------------|:-------------|:-----|:-------------|:-------------|:-----|"""
            for key, val in definition_dict.items():
                yield f"""| {key} | {val.type_name} | {val.required}| {val.default} | {val.example}| {val.description}|{val.reference}|"""
            yield ''
        else:
            yield """
| Name | Type | Required | Default | Sample | Description | Reference |
|:-------------|:-------------|:-----|:-------------|:-------------|:-----|:-----|"""
            for key, val in definition_dict.items():
                yield f"""| {key} | {val.type_name} | {val.required}| {val.default} | {val.example}| {val.description}|{val.reference}|"""
            yield ''

    def gen_example(ns, item):
        from ruamel.yaml import YAML, sys
        yaml = YAML()

        import io

        output = io.StringIO()

        sample = {
            "action": '.'.join([ns.name, item.name]),
            "inputs": {
                **pydash.map_values(pydash.get(ns, ['expects', item.func, 'inputs']),
                                    lambda x: x.example or x.default)
            },
            "params": pydash.map_values(pydash.get(ns, ['expects', item.func, 'params']), lambda x: x.example or x.default),
            "outputs": {
                **pydash.map_values(pydash.get(ns, ['expects', item.func, 'outputs']),
                                    lambda x: x.example or x.default)
            }
        }

        for k in list(sample.keys()):
            if not sample[k]:
                sample.pop(k)

        yaml.dump(sample, output)

        txt = output.getvalue()

        yield '- Sample'
        yield '```bash'
        yield indent(txt)
        yield '```'

    def gen_md():
        for key, item in ns.action_entities.items():
            doc = ns.doc_entities.get(item.func, '')
            # print(key)
            yield ''
            yield f"""## Action: {item.name}"""
            yield ''
            yield '- Description'
            yield ''
            yield trim_python_func_doc(doc)
            yield ''

            yield from gen_param_table('Inputs', pydash.get(ns, ['expects', item.func, 'inputs']) or {})
            yield from gen_param_table('Params', pydash.get(ns, ['expects', item.func, 'params']) or {})
            yield from gen_param_table('Outputs', pydash.get(ns, ['expects', item.func, 'outputs']) or {})

            yield from gen_example(ns, item)

            yield '<hr/>'

    return '\n'.join(gen_md())


def generate(api, path):
    for ns in api.namespaces:
        with pathlib.Path(path, f'{ns.name}.md').open('w') as f:
            print(doc_md(ns), file=f)

from extraction_engine.program import Program
def generate_for_program(program: Program, path):

    for ns in program.actions_by_ns.values():
        with pathlib.Path(path, f'{ns.name}.md').open('w') as f:
            print(doc_md(ns), file=f)
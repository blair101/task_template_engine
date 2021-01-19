import pathlib
import ruamel

from ruamel.yaml import YAML

from nn_project.nn_base.cfg import nn_template_strategy_dir


def migrate_strategy_template(d):
    changed = False
    def migrate_node(node):
        nonlocal changed
        if 'pipeline' in node:
            action = '.'.join([node['pipeline'], node['params']['action']])
            del node['pipeline']
            del node['params']['action']
            
            if action:
                node['action'] = action

            inputs = node['params'].pop('inputs', None)
            if inputs:
                node['inputs'] = inputs

            outputs = node['params'].pop('outputs', None)
            if outputs:
                node['outputs'] = outputs

            params = node.pop('params', None)
            if params:
                node['params'] = params

            changed = True
        elif node['type'] == 'chain':
            children = node.pop('children')
            for it in children:
                migrate_node(it)
            node['chain'] = children
            del node['type']
            changed = True
        elif node['type'] == 'any':
            children = node.pop('children')
            for it in children:
                migrate_node(it)
            node['any'] = children
            del node['type']
            changed = True
        else:
            raise ValueError('unknow object')

    for field in d.get('fields') or []:
        migrate_node(field['root'])
        field['strategy'] = field.pop('root')

    return changed

def migrate_dir(src, dst):
    pathlib.Path(dst).mkdir(parents=True, exist_ok=True)
    from tqdm.auto import tqdm
    for p in tqdm(list(pathlib.Path(src).glob('*.yaml'))):
        with p.open() as f:
            d = yaml.load(f)
        changed = migrate_strategy_template(d)

        if changed:
            with (pathlib.Path(dst) / p.name).open('w') as f:
                yaml.dump(d, f)
        else:
            print(f'{p} has no changes')

if __name__ == "__main__":
    yaml = YAML()
    # migrate_dir('/app/extraction_engine_tests/samples/program_1', '/app/extraction_engine_tests/samples/program_1')

    migrate_dir(nn_template_strategy_dir / 'nn_lc' / 'strategies', nn_template_strategy_dir / 'nn_lc' / 'strategy_templates_v2/rule_based_2')
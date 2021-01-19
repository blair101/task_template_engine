import pathlib
import yaml
import logging

logger = logging.getLogger(__name__)

def run():
    from extraction_engine.program import Program, Handler

    def load_strategy_templates():
        for it in pathlib.Path(__file__).parent.glob('*.yaml'):
            with open(it) as f:
                d = yaml.load(f)

            yield {
                "key": it.as_posix(),
                "document": d,
                "labels": {
                    "method": "rule_based",
                }
            }

    def load_actions():
        from .actions import api
        yield api

    def load_resources():
        pass

    handler = Handler()

    p = Program(load_strategy_templates, load_actions, load_resources, handler, group_by=['method'])

    # yaml_data = #load

    ret = p.run(['mean'], [1, 2, 3, 4], groups=[('rule_based', )])

    return ret
    # logger.info('Values: %s', ret.values)
import pathlib
import yaml
import logging

logger = logging.getLogger(__name__)


def run():
    from extraction_engine.program import Program

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

    p = Program(load_strategy_templates, load_actions, load_resources, group_by=['method'])

    # yaml_data = #load

    ret = p.run(fields=['mean', 'std'], document=[1, 2, 3, 4], groups=[('rule_based',)])

    return ret
    # logger.info('Values: %s', ret.values)


if __name__ == '__main__':
    from extraction_engine_tests.samples.program_1.app import run

    print("start...")

    result = run()

    print(result.values)

    # assert result.values == [
    #     {'field_code': 'pi', 'values': {}, 'group': ('rule_based',)},
    #     {'field_code': 'sum', 'values': {}, 'group': ('rule_based',)},
    #     {'field_code': 'len', 'values': {}, 'group': ('rule_based',)},
    #     {'field_code': 'mean', 'values': 2.5, 'group': ('rule_based',)},
    #     {'field_code': 'std', 'values': 1.118033988749895, 'group': ('rule_based',)},
    # ]
    #
    # assert result.failed_fields == []

    print("run end !!!")

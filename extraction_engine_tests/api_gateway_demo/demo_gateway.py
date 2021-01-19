from typing import Dict

import pydash

from extraction_engine.strategy_decorator import Namespace, Action


def extract_args(ns: Namespace, action: Action, context: Dict, params: Dict):
    expects_inputs = pydash.get(ns.expects, [action.func, 'inputs'], dict())
    expects_outputs = pydash.get(ns.expects, [action.func, 'outputs'], dict())
    expects_params = pydash.get(ns.expects, [action.func, 'params'], dict())

    args = {}

    for key, definition in expects_inputs.items():
        path = pydash.get(params, ['inputs', key], definition.default)
        value = pydash.get(context, path)
        pydash.set_(args, key, value)

    for key, definition in expects_params.items():
        value = pydash.get(params, [key], definition.default)
        pydash.set_(args, key, value)

    return args


def write_output(context, outputs, ns, action, params, status):
    expects_outputs = pydash.get(ns.expects, [action.func, 'outputs'], dict())

    for key, definition in expects_outputs.items():
        path = pydash.get(params, ['outputs', key])
        value = pydash.get(outputs, key)
        pydash.set_(context, path, value)

    pydash.set_(context, ['state', 'status'], status)
    return context


from extraction_engine.strategy_decorator import Api
class DemoApi(Api):
    def invoke(self, pipeline, action, context, yaml_params):
        params = yaml_params
        ns = self.namespace_by_name[pipeline]

        pipeline_action = ns.action_by_name[action]

        pipeline_instance = ns.get_pipeline_instance()

        args = extract_args(ns, pipeline_action, context, params)

        updated_context_ds, status = pipeline_action.func(pipeline_instance, **args)

        return_context = write_output(context, updated_context_ds, ns, pipeline_action, params, status)

        return return_context

api = DemoApi()

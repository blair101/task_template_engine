import logging
from typing import Dict

import logging
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


def test_field_extraction():
    logging.basicConfig(level=logging.DEBUG)

    from extraction_engine.strategy_decorator import Api
    class MLARAPI(Api):
        def invoke(self, pipeline, action, context, yaml_params):
            params = yaml_params
            ns = self.namespace_by_name[pipeline]

            pipeline_action = ns.action_by_name[action]

            pipeline_instance = ns.get_pipeline_instance()

            args = extract_args(ns, pipeline_action, context, params)

            updated_context_ds, status = pipeline_action.func(pipeline_instance, **args)

            return_context = write_output(context, updated_context_ds, ns, pipeline_action, params, status)

            return return_context

    api = MLARAPI()

    from extraction_engine.strategy_decorator import fields
    ns = api.namespace('flatten')  # define a pipeline

    @ns.pipeline()
    class FlattenContextTransformPipeline:

        @ns.action()
        @ns.doc("""Transform document.doc into format into a flatten form""")
        @ns.expect_inputs({
            "input": fields.Structured(default='input_a', description='input_a', required=True,
                                       example='input_a')
        })
        @ns.expect_outputs({
            "out": fields.Structured(default='out_a', description='out_a', required=True,
                                     example='out_a')
        })
        @ns.expect_params({
            "param_a": fields.Structured(default='param_a', description='param_a', required=True,
                                         example='param_a'),
            "param_b": fields.Structured(default='param_a', description='param_a', required=True,
                                         example='param_a'),
        })
        def documents_to_flatten(self, input, param_a, param_b):
            logging.info([input, param_a, param_b])
            return {
                       "out": {'1234567890': 1}
                   }, True

    result = api.invoke(pipeline='flatten',
                        action='documents_to_flatten',
                        context={"input_a": {"document": "abcde"}},
                        yaml_params={"inputs": {},
                                     "outputs": {"out": "a.b.c.d"},
                                     "param_a": "[\d+]",
                                     "param_b": 1,
                                     })

    logging.info(result)

from extraction_engine.strategy_decorator import fields
from extraction_engine_tests.api_gateway_demo.demo_gateway import api

ns = api.namespace('regex')  # define a pipeline


@ns.pipeline()
class FlattenContextTransformPipeline:
    @ns.action()
    @ns.doc("""Transform document.doc into format into a flatten form""")
    @ns.expect_inputs({
        "input": fields.Structured(default='input_a', description='input_a', required=True,
                                   example='input_a')
    })
    @ns.expect_outputs({
        "value": fields.Structured(default='', description='', required=True,
                                    example=''),

        "start": fields.Structured(default='start', description='start', required=True,
                                   example='start'),

        "end": fields.Structured(default='end', description='end', required=True,
                                 example='end')
    })
    @ns.expect_params({
        "pattern_rule": fields.Structured(default='param_a', description='param_a', required=True,
                                     example='param_a'),
    })
    def extract_pattern(self, input, pattern_rule):

        text1 = input

        import re

        pattern = re.compile(pattern_rule)

        value = pattern.findall(text1)

        pos_start = text1.find(value[0])
        pos_end = pos_start + len(value[0])

        return {
                   "value": value,
                   "start": pos_start,
                   "end": pos_end
               }, True

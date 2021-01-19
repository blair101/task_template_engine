from extraction_engine.strategy_decorator import fields
from extraction_engine_tests.sixe_field_extraction_full_demo.demo_gateway import api

ns = api.namespace('math')  # define a pipeline


@ns.pipeline()
class MathPipeline:
    @ns.action()
    @ns.doc("""Transform document.doc into format into a flatten form""")
    @ns.expect_inputs({
        "a": fields.Structured(default='input_a', description='input_a', required=True,
                                   example='input_a'),
        "b": fields.Structured(default='input_a', description='input_a', required=True,
                                   example='input_a'),
    })
    @ns.expect_outputs({
        "c": fields.Structured(default='', description='', required=True,
                                    example='')
    })
    def add(self, a, b):
        return {
                   "c": a + b
               }, True

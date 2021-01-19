from extraction_engine.strategy_decorator import Api, fields
import math
api = Api()

ns_math = api.namespace('math')


@ns_math.action_ns()
class MathActions:

    @ns_math.action(kargs_schema={"properties":{"x": {"type": "number", "default": 3.14159}}}, 
                    return_value_schema={"properties":{"x": {"type":"number"}}},
                    input_args=['x'])
    @ns_math.doc("""
    
    """)
    def pi(self, x):
        return {
            "x": x
        }, True

    @ns_math.action(kargs_schema={"properties":{"x": {"items": {"type": "number"}}}}, 
                    return_value_schema={"properties":{"x": {"type":"number"}}},
                    input_args=['x'])
    @ns_math.doc("""
    
    """)
    def sum(self, x):
        return {
            "x": sum(x)
        }, True

    @ns_math.action(kargs_schema={"properties":{"x": {"items": {"type": "number"}}}}, 
                    return_value_schema={"properties":{"x": {"type":"number"}}},
                    input_args=['x'])
    @ns_math.doc("""
    
    """)
    def std(self, x):
        m = len(x)
        mean = sum(x) / m
        acc = 0
        for i in x:
            acc += (i - mean) ** 2 / m

        return {
            "x": math.sqrt(acc)
        }, True


    @ns_math.action(kargs_schema={"properties":{"x1": {"type": "number"}, "x2": {"type": "number"}, }}, 
                    return_value_schema={"properties":{"x": {"type":"number"}}},
                    input_args=['x1', 'x2'])
    @ns_math.doc("""
    
    """)
    def divide(self, x1, x2):
        return {
            "x": x1 / x2
        }, True


ns_list = api.namespace('list')


@ns_list.pipeline()
class ListActions:

    @ns_list.action()
    @ns_list.doc("""
    
    """)
    @ns_list.expect_inputs({
        "x": fields.Raw()
    })
    @ns_list.expect_outputs({
        "x": fields.Raw()
    })
    @ns_list.expect_params({})
    def len(self, x):
        return {
            "x": len(x)
        }, True


ns_utils = api.namespace('utils')


@ns_utils.pipeline()
class UtilActions:

    @ns_utils.action()
    @ns_utils.doc("""
    
    """)
    @ns_utils.expect_inputs({
        "x": fields.Raw()
    })
    @ns_utils.expect_outputs({
        "x": fields.Raw()
    })
    @ns_utils.expect_params({})
    def write_field_value(self, x):
        return {
            "x": x
        }, True

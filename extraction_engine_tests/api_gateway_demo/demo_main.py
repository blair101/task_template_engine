import logging

from extraction_engine_tests.api_gateway_demo.demo_gateway import api

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    import extraction_engine_tests.api_gateway_demo.demo_flatten_pipeline

    # demo_flatten_pipeline.py

    result = api.invoke(pipeline='regex', # class
                        action='extract_pattern', # function
                        context={"document": {"text": "The total amount is 36744 USD"}},
                        yaml_params={"inputs": {"input":"document.text"},
                                     "outputs": {"value": "amount", "start":"position.start", "end":"position.end"},
                                     "pattern_rule": "\d+",
                                     })

    logging.info(result)

    # inputs , 参数是 路径关系， outputs 同样
    #
    # params：
    #
    #    1. input (这里就是一个输入的文本串. action:extract_pattern rename as text1 for your understanding)
    #    2. pattern_rule (是一个参数, 可以自动传入到 action:extract_pattern )
    #
    # Tips: pattern_rule 这种参数，你可以增加多个. 这里只演示一个
    #
    # result: （from api.invoke）
    #
    #    type: dict
    #
    #    content:
    #         1. context_dict,
    #         2. outputs 的结构自动组装 + status, (这部分的值 from action run result)
    #

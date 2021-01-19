import mock
from mock import MagicMock

def test_program():
    # import logging
    # logger = logging.getLogger()
    # import sys
    # handler = logging.StreamHandler(sys.stdout)
    # logger.handlers = [handler]
    # logger.setLevel(logging.INFO)
    from extraction_engine_tests.samples.program_1.app import run

    result = run()

    assert result.values == [
         {'field_code': 'pi', 'values': {}, 'group': ('rule_based', )},
         {'field_code': 'sum', 'values': {}, 'group': ('rule_based', )},
         {'field_code': 'len', 'values': {}, 'group': ('rule_based', )}, 
         {'field_code': 'mean', 'values': 2.5, 'group': ('rule_based', )}]

    assert result.failed_fields == []

def test_program_failed_fields(monkeypatch):
    # import logging
    # logger = logging.getLogger()
    # import sys
    # handler = logging.StreamHandler(sys.stdout)
    # logger.handlers = [handler]
    # logger.setLevel(logging.INFO)

    import extraction_engine.program

    _evaluate_field_strategy = extraction_engine.program.Program._evaluate_field_strategy

    mock_evaluate_field_strategy = mock.MagicMock()
    def m_evaluate_field_strategy(self, group, field_code, context):
          if field_code == 'len':
               return context, False
          else:
               return _evaluate_field_strategy(self, group, field_code, context)
       
    mock_evaluate_field_strategy.side_effect = m_evaluate_field_strategy
    monkeypatch.setattr(extraction_engine.program.Program, '_evaluate_field_strategy', m_evaluate_field_strategy)
    from extraction_engine_tests.samples.program_1.app import run

    result = run()

    assert result.values == [
         {'field_code': 'pi', 'values': {}, 'group': ('rule_based', )},
         {'field_code': 'sum', 'values': {}, 'group': ('rule_based', )},
         ]

    assert result.failed_fields == [
         {'field_code': 'len', 'cause': 'STRATEGY_FAILED', 'group': ('rule_based', )}, 
         {'field_code': 'mean', 'cause': 'DEPENDENCY_FAILED', 'group': ('rule_based', )}]

def test_program_failed_all_fields(monkeypatch):
    # import logging
    # logger = logging.getLogger()
    # import sys
    # handler = logging.StreamHandler(sys.stdout)
    # logger.handlers = [handler]
    # logger.setLevel(logging.INFO)

    import extraction_engine.program

    _evaluate_field_strategy = extraction_engine.program.Program._evaluate_field_strategy

    mock_evaluate_field_strategy = mock.MagicMock()
    def m_evaluate_field_strategy(self, group, field_code, context):
          if field_code == 'pi':
               return context, False
          else:
               return _evaluate_field_strategy(self, group, field_code, context)
       
    mock_evaluate_field_strategy.side_effect = m_evaluate_field_strategy
    monkeypatch.setattr(extraction_engine.program.Program, '_evaluate_field_strategy', m_evaluate_field_strategy)
    from extraction_engine_tests.samples.program_1.app import run

    result = run()

    assert result.values == []

    assert result.failed_fields == [
         {'field_code': 'pi', 'cause': 'STRATEGY_FAILED', 'group': ('rule_based', )},
         {'field_code': 'sum', 'cause': 'DEPENDENCY_FAILED', 'group': ('rule_based', )},
         {'field_code': 'len', 'cause': 'DEPENDENCY_FAILED', 'group': ('rule_based', )}, 
         {'field_code': 'mean', 'cause': 'DEPENDENCY_FAILED', 'group': ('rule_based', )}]
         


def test_program_filter_groups(monkeypatch):
     from extraction_engine.program import Program

     def load_templates():
          yield {
               "key": 'BKS.yaml',
               "document": {
                    "fields": [
                         {"field_code": "F_BKS_1", "strategy": {"action": "noops.noops"}},
                         {"field_code": "F_BKS_2", "strategy": {"action": "noops.noops"}},
                    ]
               },
               "labels": {
                    "method": "rule",
                    "document_type": "BKS",
                    "bank": "DBS"
               }
          }

          yield {
               "key": 'INV.yaml',
               "document": {
                    "fields": [
                         {"field_code": "F_INV_1", "strategy": {"action": "noops.noops"}},
                         {"field_code": "F_INV_2", "strategy": {"action": "noops.noops"}},
                    ]
               },
               "labels": {
                    "method": "rule",
                    "document_type": "INV",
                    "bank": "DBS"
               }
          }
     def load_actions():
          from extraction_engine.strategy_decorator import Api, Action, Namespace
          api = Api()
          noops_ns = api.namespace('noops')
          noops_ns.action('noops')(None)
          yield api
     def load_resources():
          return {}

     event_handlers = {}

     p = Program(load_templates, load_actions, load_resources, event_handlers, group_by=['method', 'document_type', 'bank'])
     p.get_all_fields() == ['F_BKS_1', 'F_BKS_2', 'F_INV_1', 'F_INV_2']
     p.get_all_fields(document_type='INV') == ['F_INV_1', 'F_INV_2']
     p.get_all_fields(document_type='BKS') == ['F_BKS_1', 'F_BKS_2']
     p.get_all_fields(document_type='BKS', method='rule') == ['F_BKS_1', 'F_BKS_2']
     p.get_all_fields(document_type='BKS', method='model') == []

     p.get_all_groups(document_type='INV') == [('rule', 'INV', 'DBS')]
     p.get_all_groups(document_type='BKS') == [('rule', 'BKS', 'DBS')]
     p.get_all_groups(document_type='INV', method='rule') == [('rule', 'INV', 'DBS')]
     p.get_all_groups(document_type='INV', method='model') == []

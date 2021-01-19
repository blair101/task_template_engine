import pytest
import textwrap
import mock
import ruamel.yaml
import io
from extraction_engine.strategy_decorator import Api, fields

@pytest.fixture(scope="session")
def validator():
    from extraction_engine.validators import ProgramValidator
    return ProgramValidator()

@pytest.fixture(scope="session")
def yaml():
    return ruamel.yaml.YAML()

def test_validators(validator, yaml, monkeypatch):
    
    api = Api()
    ns_util = api.namespace('util')
    ns_util.action('flatten')(None)

    yaml_read = textwrap.dedent("""
        fields:
        - field_code: F_AR_1
          strategy: 
            action: util.flatten
        """)
    with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
        validator.validate_program_strategy_and_actions([
            {
                "key": 'FS.yaml',
                'document': yaml.load(io.StringIO(yaml_read)),
                'labels': {
                    'method': 'rule_based',
                    'document_type': 'FS'
                }
            },
        ], [*api.namespaces], group_by=['method', 'document_type'])

    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            fields:
            - field_code: F_AR_1
              strategy: 
                action: util.flatten
                input:
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [*api.namespaces], group_by=['method', 'document_type'])


def test_validator_field_duplicates(validator, yaml, monkeypatch):
    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            fields:
            - field_code: F_AR_1
              strategy: 
                action: util.flatten
            - field_code: F_AR_1
              strategy: 
                action: util.flatten
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [], group_by=['method', 'document_type'])


def test_validator_action_ns_duplicates(validator, yaml, monkeypatch):
    from extraction_engine.strategy_decorator import Api, fields

    api_a = Api()
    api_b = Api()

    api_a.namespace('1')
    api_a.namespace('2')
    api_b.namespace('1')
    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            fields: []
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [*api_a.namespaces, *api_b.namespaces], group_by=['method', 'document_type'])


def test_validator_fields_field_missing(validator, yaml, monkeypatch):

    api_a = Api()
    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            fields: 
            - field_code: F_AR_1
              depends:
              - F_AR_0
              strategy: 
                action: util.flatten
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [], group_by=['method', 'document_type'])

    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            pre:
              base_fields:
              - F_AR_0
            fields: 
            - field_code: F_AR_1
              strategy: 
                action: util.flatten
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [], group_by=['method', 'document_type'])


def test_validator_fields_action_missing(validator, yaml, monkeypatch):
    from extraction_engine.strategy_decorator import Api, fields
    api_a = Api()
    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            fields: 
            - field_code: F_AR_1
              strategy: 
                action: util.flatten
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [*api_a.namespaces], group_by=['method', 'document_type'])

    api_a = Api()
    api_a.namespace('util')
    with pytest.raises(ValueError) as e:
        yaml_read = textwrap.dedent("""
            fields: 
            - field_code: F_AR_1
              strategy: 
                action: util.flatten
            """)
        with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
            validator.validate_program_strategy_and_actions([
                {
                    "key": 'FS.yaml',
                    'document': yaml.load(io.StringIO(yaml_read)),
                    'labels': {
                        'method': 'rule_based',
                        'document_type': 'FS'
                    }
                },
            ], [*api_a.namespaces], group_by=['method', 'document_type'])

    api_a = Api()
    ns = api_a.namespace('util')
    ns.action('flatten')(None)

    yaml_read = textwrap.dedent("""
        fields: 
        - field_code: F_AR_1
          strategy: 
            action: util.flatten
        """)
    with mock.patch('extraction_engine.validators.open', mock.mock_open(read_data=yaml_read)):
        validator.validate_program_strategy_and_actions([
            {
                "key": 'FS.yaml',
                'document': yaml.load(io.StringIO(yaml_read)),
                'labels': {
                    'method': 'rule_based',
                    'document_type': 'FS'
                }
            },
        ], [*api_a.namespaces], group_by=['method', 'document_type'])

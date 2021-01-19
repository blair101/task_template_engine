import pytest
import pathlib

@pytest.fixture()
def data_dir():
    return pathlib.Path(__file__).parent / 'data'
    
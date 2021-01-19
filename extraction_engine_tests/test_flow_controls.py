import mock

from extraction_engine.strategy_intepreter.snode_all import SNodeAll


def test_fc_all_1():
    children = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]

    children[0].transform.return_value.get.return_value = 0
    children[1].transform.return_value.get.return_value = 0
    children[2].transform.return_value.get.return_value = 1
    children[3].transform.return_value.get.return_value = 0

    context = mock.MagicMock()
    node = SNodeAll(children, definition=mock.MagicMock())
    result = node.transform(context)
    assert result == children[2].transform.return_value
    assert result != children[1].transform.return_value
    pass

def test_fc_all_2():
    children = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]

    children[0].transform.return_value.get.return_value = False
    children[1].transform.return_value.get.return_value = False
    children[2].transform.return_value.get.return_value = False
    children[3].transform.return_value.get.return_value = False

    context = mock.MagicMock()
    node = SNodeAll(children, definition=mock.MagicMock())
    result = node.transform(context)
    assert result == children[3].transform.return_value
    pass
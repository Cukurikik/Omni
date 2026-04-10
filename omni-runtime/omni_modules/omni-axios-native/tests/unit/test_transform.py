# Unit test: Transformer functions
from compute.transform import Transformer

def test_flatten():
    result = Transformer.flatten({'a': {'b': 1, 'c': {'d': 2}}})
    assert result == {'a.b': 1, 'a.c.d': 2}

def test_group_by():
    items = [{'type': 'a', 'val': 1}, {'type': 'b', 'val': 2}, {'type': 'a', 'val': 3}]
    result = Transformer.group_by(items, 'type')
    assert len(result['a']) == 2
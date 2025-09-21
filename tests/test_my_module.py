# content of test_my_module.py
from .my_module import add, subtract


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -5) == -6


def test_subtract_positive_numbers():
    assert subtract(5, 2) == 3


def test_subtract_zero():
    assert subtract(10, 0) == 10


"""
fishbone test
"""
from fishbone_diagram_generator.fishbone import Rect


def test_Rect_01():
    assert Rect(1, 2, 3, 4).get_str() == '(x,y) = (1,2) (w,h) = (3,4)'

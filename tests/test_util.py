import sys
import os

if __name__ == "__main__":
    p_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(p_dir)


import unittest

from src.util import column_header_n_select
from glob import glob


class TestUtilFunctions(unittest.TestCase):

    def test_select(self):
        select = """
        하이
        가나다 as 한글
        abc or Hi as 영어
        """
        headers, selector = column_header_n_select(select)
        # print(headers, selector)
        self.assertEqual(headers, ["하이", "한글", "영어"], "headers error")
        self.assertEqual(selector, [["하이"], ["가나다"], ["abc", "Hi"]], "selector error")

    def test_simple_select(self):
        select = "Hello"
        h, s = column_header_n_select(select)
        self.assertEqual(h[0], *s[0])

    def test_include_space(self):
        select = "n a n o"
        h, s = column_header_n_select(select)
        self.assertEqual(h[0], "n a n o")
        self.assertEqual(*s[0], "n a n o")

    def test_select_or(self):
        select = """
        A or B or C or D or E or F as Z
        """
        h, s = column_header_n_select(select)
        # print(h, s)
        self.assertEqual(len(h), 1)
        self.assertEqual(len(s[0]), 6)



if __name__ == "__main__":
    unittest.main()
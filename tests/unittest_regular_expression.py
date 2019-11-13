"""Unit tests
"""

import sys
import unittest

sys.path.insert(0, "../")

# pylint: disable wrong-import-position
from fapy.regular_expression import (
    parse_regular_expression,
    ReParser
)


class RegularExpressionTest(unittest.TestCase):

    def test_accepts_epsilon(self):
        self.assertTrue(parse_regular_expression('ε').accepts_epsilon())
        self.assertTrue(parse_regular_expression('a*').accepts_epsilon())
        self.assertTrue(parse_regular_expression('a + ε').accepts_epsilon())
        self.assertTrue(parse_regular_expression('(a + b)*').accepts_epsilon())
        self.assertFalse(parse_regular_expression('a').accepts_epsilon())
        self.assertFalse(parse_regular_expression('a* b').accepts_epsilon())

    def test_alphabet(self):
        self.assertEqual(parse_regular_expression('ε').alphabet(), set())
        self.assertEqual(parse_regular_expression('a*').alphabet(), {'a'})
        self.assertEqual(parse_regular_expression('a + ε').alphabet(), {'a'})
        self.assertEqual(parse_regular_expression('(a + b)*').alphabet(),
                         {'a', 'b'})
        self.assertEqual(parse_regular_expression('a').alphabet(), {'a'})
        self.assertEqual(parse_regular_expression('a* b').alphabet(), {'a', 'b'})


class ReParserTest(unittest.TestCase):

    def test_parse(self):
        parser = ReParser()
        problems = [
            ("ε", "ε"),
            ("a", "a"),
            ("a b", "CONCAT(a, b)"),
            ("ab", "CONCAT(a, b)"),
            ("ε b", "b"),
            ("b ε", "b"),
            ("ε b ε", "b"),
            ("ε ε ε", "ε"),
            ("a*", "STAR(a)"),
            ("a**", "STAR(a)"),
            ("a + b", "PLUS(a, b)"),
            ("(a + b)", "PLUS(a, b)"),
            ("a (a + ε) b", "CONCAT(CONCAT(a, PLUS(a, ε)), b)"),
            ("(a + b)*", "STAR(PLUS(a, b))"),
            ("(a + b*)aa b",
                "CONCAT(CONCAT(CONCAT(PLUS(a, STAR(b)), a), a), b)"),
            ("a (a + b*)*", "CONCAT(a, STAR(PLUS(a, STAR(b))))"),
            ("((a))", "a")
        ]
        for problem in problems:
            self.assertEqual(
                repr(parser.parse(problem[0])).replace(" ", ""),
                problem[1].replace(" ", "")
            )

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

"""Unit tests
"""

import unittest

# pylint: disable wrong-import-position
from fapy.regular_expression import (
    parse_regular_expression
)


class RegularExpressionTest(unittest.TestCase):

    def test___eq__(self):
        self.assertEqual(
            parse_regular_expression('a'),
            parse_regular_expression('a')
        )
        self.assertNotEqual(
            parse_regular_expression('a'),
            parse_regular_expression('b')
        )
        self.assertEqual(
            parse_regular_expression('ε'),
            parse_regular_expression('ε')
        )
        self.assertNotEqual(
            parse_regular_expression('ε'),
            parse_regular_expression('b')
        )
        self.assertEqual(
            parse_regular_expression('a + b'),
            parse_regular_expression('a + b')
        )
        self.assertNotEqual(
            parse_regular_expression('a'),
            parse_regular_expression('a + b')
        )
        self.assertNotEqual(
            parse_regular_expression('b + a'),
            parse_regular_expression('a + b')
        )
        self.assertEqual(
            parse_regular_expression('(a + b)* c'),
            parse_regular_expression('(a + b)* c')
        )
        self.assertNotEqual(
            parse_regular_expression('(a + b)* c'),
            parse_regular_expression('a* c')
        )
        self.assertNotEqual(
            parse_regular_expression('(a + b)* c'),
            parse_regular_expression('(a + b) c')
        )



    def test_accepting_letters(self):
        self.assertEqual(
            parse_regular_expression("ε").accepting_letters(),
            set()
        )
        self.assertEqual(
            parse_regular_expression("a").accepting_letters(),
            {'a'}
        )
        self.assertEqual(
            parse_regular_expression("a b").accepting_letters(),
            {'b'}
        )
        self.assertEqual(
            parse_regular_expression("a + b").accepting_letters(),
            {'a', 'b'}
        )
        self.assertEqual(
            parse_regular_expression("a* b").accepting_letters(),
            {'b'}
        )
        self.assertEqual(
            parse_regular_expression("a b*").accepting_letters(),
            {'a', 'b'}
        )
        self.assertEqual(
            parse_regular_expression("(a + b)* (c + ε)").accepting_letters(),
            {'a', 'b', 'c'}
        )
        self.assertEqual(
            parse_regular_expression("(c + ε) (a + b)*").accepting_letters(),
            {'a', 'b', 'c'}
        )

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

    def test_initial_letters(self):
        self.assertEqual(
            parse_regular_expression("ε").initial_letters(),
            set()
        )
        self.assertEqual(
            parse_regular_expression("a").initial_letters(),
            {'a'}
        )
        self.assertEqual(
            parse_regular_expression("a b").initial_letters(),
            {'a'}
        )
        self.assertEqual(
            parse_regular_expression("a + b").initial_letters(),
            {'a', 'b'}
        )
        self.assertEqual(
            parse_regular_expression("a* b").initial_letters(),
            {'a', 'b'}
        )
        self.assertEqual(
            parse_regular_expression("a b*").initial_letters(),
            {'a'}
        )
        self.assertEqual(
            parse_regular_expression("(a + b)* (c + ε)").initial_letters(),
            {'a', 'b', 'c'}
        )
        self.assertEqual(
            parse_regular_expression("(c + ε) (a + b)*").initial_letters(),
            {'a', 'b', 'c'}
        )

    def test_successors(self):
        re1 = parse_regular_expression('a b')
        self.assertEqual(re1.successors('a'), {'b'})
        self.assertEqual(re1.successors('b'), set())
        self.assertEqual(re1.successors('c'), set())
        re2 = parse_regular_expression('(a + b)*')
        self.assertEqual(re2.successors('a'), {'a', 'b'})
        self.assertEqual(re2.successors('b'), {'a', 'b'})
        self.assertEqual(re2.successors('c'), set())
        re3 = parse_regular_expression('a b a c')
        self.assertEqual(re3.successors('a'), {'b', 'c'})
        self.assertEqual(re3.successors('b'), {'a'})
        self.assertEqual(re3.successors('c'), set())
        re4 = parse_regular_expression('(a b)* (c + ε) d')
        self.assertEqual(re4.successors('a'), {'b'})
        self.assertEqual(re4.successors('b'), {'a', 'c', 'd'})
        self.assertEqual(re4.successors('c'), {'d'})
        self.assertEqual(re4.successors('d'), set())
        re5 = parse_regular_expression('(a+ε)(b+ε)(c+ε)(d+ε)')
        self.assertEqual(re5.successors('a'), {'b', 'c', 'd'})
        self.assertEqual(re5.successors('b'), {'c', 'd'})
        self.assertEqual(re5.successors('c'), {'d'})
        self.assertEqual(re5.successors('d'), set())
        re6 = parse_regular_expression('(a (bc)*)*')
        self.assertEqual(re6.successors('a'), {'a', 'b'})
        self.assertEqual(re6.successors('b'), {'c'})
        self.assertEqual(re6.successors('c'), {'a', 'b'})



class ReParserTest(unittest.TestCase):

    def test_parse(self):
        problems = [
            ("ε", "ε"),
            ("a", "a"),
            ("a b", "CONCAT(a, b)"),
            ("ab", "CONCAT(a, b)"),
            ("ε b", "b"),
            ("b ε", "b"),
            ("ε b ε", "b"),
            ("ε ε ε", "ε"),
            ("b ε ε", "b"),
            ("a*", "STAR(a)"),
            ("a**", "STAR(a)"),
            ("a + b", "PLUS(a, b)"),
            ("(a + b)", "PLUS(a, b)"),
            ("a + ab", "PLUS(a, CONCAT(a, b))"),
            ("ba + ab", "PLUS(CONCAT(b, a), CONCAT(a, b))"),
            ("a (a + ε) b", "CONCAT(CONCAT(a, PLUS(a, ε)), b)"),
            ("(a + b)*", "STAR(PLUS(a, b))"),
            ("(a + b*)aa b",
             "CONCAT(CONCAT(CONCAT(PLUS(a, STAR(b)), a), a), b)"),
            ("a (a + b*)*", "CONCAT(a, STAR(PLUS(a, STAR(b))))"),
            ("((a))", "a")
        ]
        for problem, solution in problems:
            self.assertEqual(
                repr(parse_regular_expression(problem)).replace(" ", ""),
                solution.replace(" ", ""),
                f'Failed regular expression: {problem}'
            )

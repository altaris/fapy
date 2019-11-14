"""Unit tests
"""

import unittest

# pylint: disable wrong-import-position
from fapy.algorithm_glushkov import (
    _linearize_regular_expression,
    glushkov
)
from fapy.regular_expression import (
    parse_regular_expression
)

class GlushkovTest(unittest.TestCase):

    def test__linearize_regular_expression(self):
        re1 = parse_regular_expression('a (a + b + ε)* a')
        lin1, idx1 = _linearize_regular_expression(re1)
        self.assertEqual(idx1, 4)
        self.assertEqual(len(lin1.alphabet()), 4)
        self.assertEqual(
            repr(lin1).replace(' ', ''),
            'CONCAT(CONCAT(a0, STAR(PLUS(PLUS(a1, b2), ε))), a3)'
                .replace(' ', '')
        )
        re2 = parse_regular_expression('a a a a a a a')
        lin2, idx2 = _linearize_regular_expression(re2)
        self.assertEqual(idx2, 7)
        self.assertEqual(len(lin2.alphabet()), 7)

    def test_glushkov(self):
        aut1 = glushkov(parse_regular_expression('a b'))
        aut1.draw(
            name='GlushkovTest.test_glushkov.1'
        ).render(directory='out/', format='pdf')
        self.assertTrue(aut1.read("ab"))
        self.assertFalse(aut1.read(""))
        self.assertFalse(aut1.read("a"))
        self.assertFalse(aut1.read("b"))
        self.assertFalse(aut1.read("ba"))
        self.assertFalse(aut1.read("aba"))

        aut2 = glushkov(parse_regular_expression('(a b)* (c + ε) d'))
        aut2.draw(
            name='GlushkovTest.test_glushkov.2'
        ).render(directory='out/', format='pdf')
        self.assertTrue(aut2.read("d"))
        self.assertTrue(aut2.read("abababd"))
        self.assertTrue(aut2.read("ababcd"))
        self.assertFalse(aut2.read(""))
        self.assertFalse(aut2.read("ab"))
        self.assertFalse(aut2.read("abccd"))
        self.assertFalse(aut2.read("ccd"))

        aut3 = glushkov(parse_regular_expression('(a (ab)*)*'))
        aut3.draw(
            name='GlushkovTest.test_glushkov.3'
        ).render(directory='out/', format='pdf')
        self.assertTrue(aut3.read(""))
        self.assertTrue(aut3.read("aaaaaa"))
        self.assertTrue(aut3.read("aababaaaabab"))
        self.assertFalse(aut3.read("b"))
        self.assertFalse(aut3.read("bab"))

        aut4 = glushkov(parse_regular_expression('(a (b + (bbabb))* c)*'))
        aut4.draw(
            name='GlushkovTest.test_glushkov.4'
        ).render(directory='out/', format='pdf')
        self.assertTrue(aut4.read(""))
        self.assertTrue(aut4.read("ac"))
        self.assertTrue(aut4.read("acac"))
        self.assertTrue(aut4.read("abbcabbabbc"))
        self.assertFalse(aut4.read("aac"))
        self.assertFalse(aut4.read("abbabc"))

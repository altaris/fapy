"""Unit tests
"""

import sys
import unittest

sys.path.insert(0, "../")

# pylint: disable wrong-import-position
from fapy.algorithm_glushkov import (
    _accepting_letters,
    _initial_letters,
    _linearize_regular_expression,
    _successors,
    glushkov
)
from fapy.regular_expression import (
    parse_regular_expression
)

class GlushkovTest(unittest.TestCase):

    def test__accepting_letters(self):
        self.assertEqual(
            _accepting_letters(parse_regular_expression("ε")),
            set()
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("a")),
            {'a'}
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("a b")),
            {'b'}
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("a + b")),
            {'a', 'b'}
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("a* b")),
            {'b'}
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("a b*")),
            {'a', 'b'}
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("(a + b)* (c + ε)")),
            {'a', 'b', 'c'}
        )
        self.assertEqual(
            _accepting_letters(parse_regular_expression("(c + ε) (a + b)*")),
            {'a', 'b', 'c'}
        )

    def test__initial_letters(self):
        self.assertEqual(
            _initial_letters(parse_regular_expression("ε")),
            set()
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("a")),
            {'a'}
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("a b")),
            {'a'}
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("a + b")),
            {'a', 'b'}
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("a* b")),
            {'a', 'b'}
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("a b*")),
            {'a'}
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("(a + b)* (c + ε)")),
            {'a', 'b', 'c'}
        )
        self.assertEqual(
            _initial_letters(parse_regular_expression("(c + ε) (a + b)*")),
            {'a', 'b', 'c'}
        )

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

    def test__successors(self):
        re1 = parse_regular_expression('a b')
        self.assertEqual(_successors(re1, 'a'), {'b'})
        self.assertEqual(_successors(re1, 'b'), set())
        self.assertEqual(_successors(re1, 'c'), set())
        re2 = parse_regular_expression('(a + b)*')
        self.assertEqual(_successors(re2, 'a'), {'a', 'b'})
        self.assertEqual(_successors(re2, 'b'), {'a', 'b'})
        self.assertEqual(_successors(re2, 'c'), set())
        re3 = parse_regular_expression('a b a c')
        self.assertEqual(_successors(re3, 'a'), {'b', 'c'})
        self.assertEqual(_successors(re3, 'b'), {'a'})
        self.assertEqual(_successors(re3, 'c'), set())
        re4 = parse_regular_expression('(a b)* (c + ε) d')
        self.assertEqual(_successors(re4, 'a'), {'b'})
        self.assertEqual(_successors(re4, 'b'), {'a', 'c', 'd'})
        self.assertEqual(_successors(re4, 'c'), {'d'})
        self.assertEqual(_successors(re4, 'd'), set())
        re5 = parse_regular_expression('(a+ε)(b+ε)(c+ε)(d+ε)')
        self.assertEqual(_successors(re5, 'a'), {'b', 'c', 'd'})
        self.assertEqual(_successors(re5, 'b'), {'c', 'd'})
        self.assertEqual(_successors(re5, 'c'), {'d'})
        self.assertEqual(_successors(re5, 'd'), set())
        re6 = parse_regular_expression('(a (bc)*)*')
        self.assertEqual(_successors(re6, 'a'), {'a', 'b'})
        self.assertEqual(_successors(re6, 'b'), {'c'})
        self.assertEqual(_successors(re6, 'c'), {'a', 'b'})

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

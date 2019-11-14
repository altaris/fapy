"""Unit tests
"""

import unittest

# pylint: disable wrong-import-position
from fapy.algorithm_thompson import (
    thompson
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    parse_regular_expression,
    RegularExpression
)


class ThompsonTest(unittest.TestCase):

    def test_thompson_letter(self):
        alphabet = {'a', 'b'}
        automaton = thompson(parse_regular_expression('a'), alphabet)
        automaton.draw(
            name='ThompsonTest.test_thompson_letter'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton.read('a'))
        self.assertFalse(automaton.read('b'))
        self.assertFalse(automaton.read(''))

    def test_thompson_plus(self):
        alphabet = {'a', 'b'}
        automaton = thompson(parse_regular_expression('a + b'), alphabet)
        automaton.draw(
            name='ThompsonTest.test_thompson_plus'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton.read('a'))
        self.assertTrue(automaton.read('b'))
        self.assertFalse(automaton.read(''))
        self.assertFalse(automaton.read('ab'))

    def test_thompson_concat(self):
        alphabet = {'a', 'b'}
        automaton = thompson(parse_regular_expression('a b a'), alphabet)
        automaton.draw(
            name='ThompsonTest.test_thompson_concat'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton.read('aba'))
        self.assertFalse(automaton.read(''))
        self.assertFalse(automaton.read('a'))
        self.assertFalse(automaton.read('b'))
        self.assertFalse(automaton.read('ab'))
        self.assertFalse(automaton.read('ba'))
        self.assertFalse(automaton.read('aaaaaba'))

    def test_thompson_star(self):
        alphabet = {'a', 'b'}
        automaton = thompson(
            parse_regular_expression('((a + b) b)*'),
            alphabet)
        automaton.draw(
            name='ThompsonTest.test_thompson_star'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton.read(''))
        self.assertTrue(automaton.read('ab'))
        self.assertTrue(automaton.read('bb'))
        self.assertTrue(automaton.read('abbb'))
        self.assertTrue(automaton.read('abababababababab'))
        self.assertFalse(automaton.read('a'))
        self.assertFalse(automaton.read('aa'))
        self.assertFalse(automaton.read('abbbaa'))

    def test_thompson_1(self):
        alphabet = {'a', 'b'}
        automaton = thompson(
            parse_regular_expression('(a + b)* a (a + b)*'),
            alphabet
        )
        automaton.draw(
            name='ThompsonTest.test_thompson_1'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton.read('a'))
        self.assertTrue(automaton.read('aa'))
        self.assertTrue(automaton.read('aba'))
        self.assertTrue(automaton.read('bbbbbba'))
        self.assertTrue(automaton.read('bbbbbbab'))
        self.assertFalse(automaton.read('bb'))
        self.assertFalse(automaton.read(''))
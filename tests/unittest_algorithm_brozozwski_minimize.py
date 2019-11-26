# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

"""Unit tests
"""

import unittest

from fapy.algorithm_brozozwski_minimize import (
    brozozwski_minimize,
    transpose
)
from fapy.algorithm_thompson import (
    thompson
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    parse_regular_expression
)

class BrozozwskiMinimizeTest(unittest.TestCase):

    def test_brozozwski_minimize(self):
        alphabet = {'a', 'b', 'c', 'd'}
        automaton1 = brozozwski_minimize(
            thompson(parse_regular_expression('abcd'), alphabet)
        )
        automaton1.draw(
            name='BrozozwskiMinimizeTest.test_brozozwski_minimize.automaton1'
        ).render(directory='out/', format='pdf')
        self.assertEqual(len(automaton1.states), 5)
        self.assertTrue(automaton1.read('abcd'))
        self.assertFalse(automaton1.read('a'))
        self.assertFalse(automaton1.read('ab'))
        self.assertFalse(automaton1.read('abc'))
        self.assertFalse(automaton1.read('bcda'))
        self.assertFalse(automaton1.read('dcbaa'))

    def test_transpose(self):
        automaton1 = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q2'},
            transitions={
                'q0':[('a', 'q1')],
                'q1':[('b', 'q2')]
            }
        )
        transposed_automaton1 = transpose(automaton1)
        self.assertTrue(transposed_automaton1.read('ba'))
        self.assertFalse(transposed_automaton1.read(''))
        self.assertFalse(transposed_automaton1.read('a'))
        self.assertFalse(transposed_automaton1.read('b'))
        self.assertFalse(transposed_automaton1.read('aa'))
        self.assertFalse(transposed_automaton1.read('ab'))
        self.assertFalse(transposed_automaton1.read('bb'))

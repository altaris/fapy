"""Unit tests
"""

from typing import (
    List
)
import unittest

# pylint: disable wrong-import-position
from fapy.algorithm_brozozwski import (
    brozozwski
)
from fapy.algorithm_thompson import (
    thompson
)
from fapy.common import (
    Word
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    parse_regular_expression,
)


class BrozozwskiTest(unittest.TestCase):

    def _compare(
            self,
            automaton1: FiniteAutomaton,
            automaton2: FiniteAutomaton,
            word_list: List[Word]):
        for word in word_list:
            self.assertEqual(
                automaton1.read(word),
                automaton2.read(word),
                f'Failed word: "{word}"'
            )

    def test_brozozwski(self):

        alphabet = {'a', 'b', 'c'}

        aut1 = FiniteAutomaton(
            alphabet=alphabet,
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q1')]
            }
        )
        self.assertEqual(
            repr(brozozwski(aut1)).replace(' ', ''),
            'a'.replace(' ', '')
        )

        aut2 = FiniteAutomaton(
            alphabet=alphabet,
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q2'},
            transitions={
                'q0': [('a', 'q1')],
                'q1': [('b', 'q2')]
            }
        )
        self.assertEqual(
            repr(brozozwski(aut2)).replace(' ', ''),
            'CONCAT(a, b)'.replace(' ', '')
        )

        aut2 = FiniteAutomaton(
            alphabet=alphabet,
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q2'},
            transitions={
                'q0': [('a', 'q1'), ('c', 'q2')],
                'q1': [('b', 'q2')]
            }
        )
        aut2_bro = brozozwski(aut2)
        aut2_rec = thompson(aut2_bro, alphabet)
        self._compare(
            aut2,
            aut2_rec,
            ['', 'a', 'b', 'c', 'ab', 'abc']
        )

        aut3 = FiniteAutomaton(
            alphabet=alphabet,
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q2'},
            transitions={
                'q0': [('a', 'q0'), ('b', 'q1')],
                'q1': [('c', 'q2')]
            }
        )
        aut3_bro = brozozwski(aut3)
        aut3_rec = thompson(aut3_bro, alphabet)
        self._compare(
            aut3,
            aut3_rec,
            ['', 'a', 'b', 'c', 'ab', 'abc', 'aaab']
        )

        aut4 = FiniteAutomaton(
            alphabet=alphabet,
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q0'},
            transitions={
                'q0': [('a', 'q1')],
                'q1': [('a', 'q2')],
                'q1': [('a', 'q0')]
            }
        )
        aut4_bro = brozozwski(aut4)
        aut4_rec = thompson(aut4_bro, alphabet)
        self._compare(
            aut4,
            aut4_rec,
            ['', 'a', 'b', 'c', 'aa', 'aab', 'aaa', 'aaaa', 'aaaaaa']
        )

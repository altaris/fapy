"""Unit tests
"""

import sys
import unittest

sys.path.insert(0, "../")

# pylint: disable wrong-import-position
from fapy.finite_automaton import (
    FiniteAutomaton
)


class FiniteAutomatonTest(unittest.TestCase):

    def test___init__(self):
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={},
                states={'q0'},
                initial_states={},
                accepting_states={},
                transitions=[]
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'INVALID'},
                accepting_states={},
                transitions=[]
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'q0'},
                accepting_states={'INVALID'},
                transitions=[]
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'q0'},
                accepting_states={'q0'},
                transitions={
                    'q0': [('INVALID', 'q0')]
                }
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'q0'},
                accepting_states={'q0'},
                transitions={
                    'q0': [('a', 'INVALID')]
                }
            )
        FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q1'), ('b', 'q0')],
                'q1': [('a', 'q1'), ('b', 'q0')]
            }
        )

    def test_draw(self):
        dfa = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q1'), ('b', 'q0')],
                'q1': [('a', 'q1'), ('b', 'q0')]
            }
        )
        ndfa = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q0'), ('b', 'q0'), ('a', 'q1')],
                'q1': [('a', 'q1'), ('b', 'q1')]
            }
        )
        dfa.draw(
            name='FiniteAutomatonTest.test_draw.dfa'
        ).render(directory='out/', format='pdf')
        ndfa.draw(
            name='FiniteAutomatonTest.test_draw.ndfa'
        ).render(directory='out/', format='pdf')

    def test_is_deterministic(self):
        dfa = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q1'), ('b', 'q0')],
                'q1': [('a', 'q1'), ('b', 'q0')]
            }
        )
        ndfa = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q0'), ('b', 'q0'), ('a', 'q1')],
                'q1': [('a', 'q1'), ('b', 'q1')]
            }
        )
        self.assertTrue(dfa.is_deterministic())
        self.assertFalse(ndfa.is_deterministic())

    def test_read(self):
        ndfa = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('a', 'q0'), ('b', 'q0'), ('a', 'q1')],
                'q1': [('a', 'q1'), ('b', 'q1')]
            }
        )
        with self.assertRaises(ValueError):
            ndfa.read(['a', 'INVALID'])
        self.assertTrue(ndfa.read(['a']))
        self.assertTrue(ndfa.read(['a', 'a']))
        self.assertTrue(ndfa.read(['a', 'b', 'a']))
        self.assertTrue(ndfa.read(['a', 'b', 'b']))
        self.assertFalse(ndfa.read([]))
        self.assertFalse(ndfa.read(['b']))
        self.assertFalse(ndfa.read(['b', 'b']))
        self.assertFalse(ndfa.read(['b', 'b', 'b']))

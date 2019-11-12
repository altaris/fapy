"""Unit tests
"""

import sys
import unittest

sys.path.insert(0, "../")

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
                transitions={}
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'INVALID'},
                accepting_states={},
                transitions={}
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'q0'},
                accepting_states={'INVALID'},
                transitions={}
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'q0'},
                accepting_states={'q0'},
                transitions={
                    'q0': {'INVALID': 'q0'}
                }
            )
        with self.assertRaises(ValueError):
            FiniteAutomaton(
                alphabet={'a'},
                states={'q0'},
                initial_states={'q0'},
                accepting_states={'q0'},
                transitions={
                    'q0': {'a': 'INVALID'}
                }
            )
        FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': {'a': 'q1', 'b': 'q0'},
                'q1': {'a': 'q1', 'b': 'q0'}
            }
        )

"""Unit tests
"""

import unittest

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

    def test_epsilon_closure(self):
        automaton = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5'},
            initial_states={'q0'},
            accepting_states={'q0'},
            transitions={
                'q0': [('a', 'q4'), ('ε', 'q1')],
                'q2': [('ε', 'q3')],
                'q3': [('ε', 'q4')],
                'q5': [('ε', 'q4')]
            }
        )
        self.assertEqual(automaton.epsilon_closure({'q0'}), {'q0', 'q1'})
        self.assertEqual(automaton.epsilon_closure({'q1'}), {'q1'})
        self.assertEqual(automaton.epsilon_closure({'q2'}), {'q2', 'q3', 'q4'})
        self.assertEqual(automaton.epsilon_closure({'q3'}), {'q3', 'q4'})
        self.assertEqual(automaton.epsilon_closure({'q4'}), {'q4'})
        self.assertEqual(automaton.epsilon_closure({'q5'}), {'q4', 'q5'})

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
        ndfae = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1'},
            initial_states={'q0'},
            accepting_states={'q1'},
            transitions={
                'q0': [('ε', 'q1'), ('b', 'q0')],
                'q1': [('a', 'q1'), ('b', 'q0')]
            }
        )
        self.assertTrue(dfa.is_deterministic())
        self.assertFalse(ndfa.is_deterministic())
        self.assertFalse(ndfae.is_deterministic())

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
        ndfae = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q2'},
            transitions={
                'q0': [('a', 'q0'), ('b', 'q0'), ('a', 'q1')],
                'q1': [('a', 'q0'), ('b', 'q0'), ('ε', 'q2')]
            }
        )
        ndfae2 = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q0', 'q1', 'q2'},
            initial_states={'q0'},
            accepting_states={'q2'},
            transitions={
                'q0': [('ε', 'q1')],
                'q1': [('ε', 'q2')]
            }
        )

        self.assertTrue(ndfa.read('a'))
        self.assertTrue(ndfa.read('aa'))
        self.assertTrue(ndfa.read('aba'))
        self.assertTrue(ndfa.read('abb'))
        self.assertFalse(ndfa.read(''))
        self.assertFalse(ndfa.read('b'))
        self.assertFalse(ndfa.read('bb'))
        self.assertFalse(ndfa.read('bbb'))

        self.assertTrue(ndfae.read('a'))
        self.assertTrue(ndfae.read('aa'))
        self.assertTrue(ndfae.read('aaa'))
        self.assertTrue(ndfae.read('aba'))
        self.assertTrue(ndfae.read('bba'))

        self.assertFalse(ndfae.read('b'))
        self.assertTrue(ndfae2.read(''))

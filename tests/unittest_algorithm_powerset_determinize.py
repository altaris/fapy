# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

"""Unit tests
"""

import unittest

# pylint: disable wrong-import-position
from fapy.algorithm_powerset_determinize import (
    powerset_determinize
)
from fapy.finite_automaton import (
    FiniteAutomaton
)


class PowerSetDeterminizeTest(unittest.TestCase):

    def test_powerset_determinize(self):
        ndfa = FiniteAutomaton(
            alphabet={'a', 'b'},
            states={'q-1', 'q0', 'q1', 'q2'},
            initial_states={'q-1'},
            accepting_states={'q2'},
            transitions={
                'q-1': [('ε', 'q0')],
                'q0': [('a', 'q0'), ('b', 'q0'), ('a', 'q1')],
                'q1': [('a', 'q1'), ('b', 'q1'), ('ε', 'q2')]
            }
        )
        det_ndfa = powerset_determinize(ndfa)
        self.assertTrue(det_ndfa.is_deterministic())
        ndfa.draw(
            name='PowerSetDeterminizeTest.test_powerset_determinize.ndfa'
        ).render(directory='out/', format='pdf')
        det_ndfa.draw(
            name='PowerSetDeterminizeTest.test_powerset_determinize.det_ndfa'
        ).render(directory='out/', format='pdf')

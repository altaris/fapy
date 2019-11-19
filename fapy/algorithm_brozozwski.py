"""Implementation of Brozozwski's algorithm for regular expressions

Brozozwski's algorithm transforms a finite automaton into an equivalent regular
expression by iteratively removing states.

Example: consider::

    automaton = FiniteAutomaton(
        alphabet={'a', 'b'},
        states={'q0', 'q1', 'q2', 'q3'},
        initial_states={'q0'},
        accepting_states={'q3'},
        transitions={
            'q0': [('a', 'q1'), ('b', 'q3')],
            'q1': [('a', 'q2')],
            'q2': [('a', 'q0')]
        }
    )

The automaton recognizes all words starting with a number of :math:`a` that is
a multiple of :math:`3`, and finishes with a :math:`b`. As expected, this
snippet prints ``(a a a)* b``.

Warning:
    This is not Brozozwski's minimization algorithm.
"""

from typing import (
    Dict
)


from fapy.common import (
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    parse_regular_expression,
    RegularExpression
)


def _concat(left: str, right: str) -> str:
    """Convenience function

    Takes two string representations of regular expressions, where the empty
    string is considered as matching the empty langage, and returns a string
    representation of their concatenation.
    """
    if len(left) > 0 and len(right) > 0:
        return left + right
    return ''


def _plus(left: str, right: str) -> str:
    """Convenience function

    Takes two string representations of regular expressions, where the empty
    string is considered as matching the empty langage, and returns a string
    representation of their sum.
    """
    if len(left) > 0 and len(right) > 0:
        return left + '+' + right
    if len(left) > 0:
        return left
    return right


def _star(inner: str) -> str:
    """Convenience function

    Takes a string representations of a regular expression, where the empty
    string is considered as matching the empty langage, and returns its star
    regular expression.
    """
    if len(inner) > 0:
        return f'({inner})*'
    return 'ε'


def brozozwski(automaton: FiniteAutomaton) -> RegularExpression:
    """Implementation of Brozozwski's algorithm for regular expressions
    """

    q_init = 'init'
    q_acc = 'acc'
    table: Dict[State, Dict[State, str]] = {
        q_acc: {},
        q_init: {}
    }
    for state in automaton.initial_states:
        table[q_init][state] = 'ε'
    for state in automaton.states:
        table[state] = {}
        for letter, next_state in automaton.transitions.get(state, []):
            if next_state in table[state]:
                table[state][next_state] += '+' + letter
            else:
                table[state][next_state] = letter
    for state in automaton.accepting_states:
        table[state][q_acc] = 'ε'

    states_to_remove = list(automaton.states)
    states_to_remove.sort()
    while states_to_remove:
        q_i = states_to_remove.pop()
        for q_k in states_to_remove + [q_init, q_acc]:
            if q_k == q_i:
                continue
            for q_l in states_to_remove + [q_init, q_acc]:
                if q_l == q_i:
                    continue
                e_kl = table[q_k].get(q_l, '')
                e_ki = table[q_k].get(q_i, '')
                e_ii = table[q_i].get(q_i, '')
                e_il = table[q_i].get(q_l, '')
                table[q_k][q_l] = _plus(
                    e_kl,
                    _concat(
                        _concat(
                            e_ki,
                            _star(e_ii)
                        ),
                        e_il
                    )
                )

    return parse_regular_expression(table[q_init].get(q_acc, ''))

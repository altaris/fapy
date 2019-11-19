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
    print(brozozwski(automaton))

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
    empty_word_automaton,
    FiniteAutomaton
)
from fapy.regular_expression import (
    parse_regular_expression,
    RegularExpression
)


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
        qi = states_to_remove.pop()
        for qk in states_to_remove + [q_init, q_acc]:
            if qk == qi:
                continue
            for ql in states_to_remove + [q_init, q_acc]:
                if ql == qi:
                    continue
                e_kl = table[qk].get(ql, '')
                e_ki = table[qk].get(qi, '')
                e_ii = table[qi].get(qi, '')
                e_il = table[qi].get(ql, '')
                e_kil = ''
                if e_ii:
                    e_ii = '(' + e_ii + ')*'
                if len(e_ki) > 0 and len(e_il) > 0:
                    e_kil = e_ki + e_ii + e_il
                if len(e_kl) > 0 and len(e_kil) > 0:
                    table[qk][ql] = f'({e_kl})+({e_kil})'
                elif not e_kl:
                    table[qk][ql] = e_kil
                else:
                    table[qk][ql] = e_kl

    return parse_regular_expression(table[q_init].get(q_acc, ''))

"""Transforms a regular expression into an equivalent automaton using
Thompson's algorithm.
"""

from fapy.common import (
    Alphabet,
    Letter,
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    RegularExpression
)


def thompson(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:

    if regular_expression.node_type == 'CONCAT':
        if not regular_expression.left:
            raise ValueError("This should not happen :/")
        if not regular_expression.right:
            raise ValueError("This should not happen :/")
        left = thompson(regular_expression.left, alphabet, index)
        index += len(left.states)
        right = thompson(regular_expression.right, alphabet, index)
        left_q = list(left.accepting_states)[0]
        right_q = list(right.initial_states)[0]
        return FiniteAutomaton(
            alphabet=alphabet,
            states=left.states | right.states,
            initial_states=left.initial_states,
            accepting_states=right.accepting_states,
            transitions={
                **left.transitions,
                **right.transitions,
                left_q: [('ε', right_q)]
            }
        )

    elif regular_expression.node_type == 'EPSILON':
        q0 = f'q{index}'
        q1 = f'q{index + 1}'
        return FiniteAutomaton(
            alphabet=alphabet,
            states={q0, q1},
            initial_states={q0},
            accepting_states={q1},
            transitions={q0: [('ε', q1)]}
        )

    elif regular_expression.node_type == 'LETTER':
        if not regular_expression.letter:
            raise ValueError("This should not happen :/")
        q0 = f'q{index}'
        q1 = f'q{index + 1}'
        return FiniteAutomaton(
            alphabet=alphabet,
            states={q0, q1},
            initial_states={q0},
            accepting_states={q1},
            transitions={q0: [(regular_expression.letter, q1)]}
        )

    elif regular_expression.node_type == 'PLUS':
        if not regular_expression.left:
            raise ValueError("This should not happen :/")
        if not regular_expression.right:
            raise ValueError("This should not happen :/")
        left = thompson(regular_expression.left, alphabet, index)
        index += len(left.states)
        right = thompson(regular_expression.right, alphabet, index)
        index += len(right.states)
        q_init_left = list(left.initial_states)[0]
        q_acc_left = list(left.accepting_states)[0]
        q_init_right = list(right.initial_states)[0]
        q_acc_right = list(right.accepting_states)[0]
        q_init = f'q{index}'
        q_acc = f'q{index + 1}'
        transitions = {
            **left.transitions,
            **right.transitions,
            q_init: [('ε', q_init_left), ('ε', q_init_right)],
        }
        if q_acc_left not in transitions:
            transitions[q_acc_left] = []
        transitions[q_acc_left].append(('ε', q_acc))
        if q_acc_right not in transitions:
            transitions[q_acc_right] = []
        transitions[q_acc_right].append(('ε', q_acc))
        return FiniteAutomaton(
            alphabet=alphabet,
            states=left.states | right.states | {q_init, q_acc},
            initial_states={q_init},
            accepting_states={q_acc},
            transitions=transitions
        )

    elif regular_expression.node_type == 'STAR':
        if not regular_expression.inner:
            raise ValueError("This should not happen :/")
        inner = thompson(regular_expression.inner, alphabet, index)
        index += len(inner.states)
        q_init_inner = list(inner.initial_states)[0]
        q_acc_inner = list(inner.accepting_states)[0]
        q_init = f'q{index}'
        q_acc = f'q{index + 1}'
        transitions = {
            **inner.transitions,
            q_init: [('ε', q_init_inner), ('ε', q_acc)],
        }
        if q_acc_inner not in transitions:
            transitions[q_acc_inner] = []
        transitions[q_acc_inner].append(('ε', q_init_inner))
        transitions[q_acc_inner].append(('ε', q_acc))
        return FiniteAutomaton(
            alphabet=alphabet,
            states=inner.states | {q_init, q_acc},
            initial_states={q_init},
            accepting_states={q_acc},
            transitions=transitions
        )

    else:
        raise ValueError(f'Unknown node type {regular_expression.node_type}')

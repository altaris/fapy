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


def _concatenation_automaton(*args) -> FiniteAutomaton:
    """Concatenates several automata (at least 1).
    """
    if not args:
        raise ValueError("Expected at least 1 automaton")
    if len(args) == 1:
        return args[0]
    args_list = list(args)
    left = args_list.pop(0)
    right = _concatenation_automaton(*args_list)
    result = FiniteAutomaton(
        alphabet=left.alphabet | right.alphabet,
        states=left.states | right.states,
        initial_states=left.initial_states,
        accepting_states=right.accepting_states,
        transitions={
            **left.transitions,
            **right.transitions
        }
    )
    for q_acc_left in left.accepting_states:
        if q_acc_left not in result.transitions:
            result.transitions[q_acc_left] = []
        for q_init_right in right.initial_states:
            result.transitions[q_acc_left].append(('ε', q_init_right))
    return result


def _disjoint_union_automaton(*args) -> FiniteAutomaton:
    """Returns the disjoint union of several automata (at least 1)
    """
    if not args:
        raise ValueError("Expected at least 1 automaton")
    if len(args) == 1:
        return args[0]
    args_list = list(args)
    left = args_list.pop(0)
    right = _disjoint_union_automaton(*args_list)
    return FiniteAutomaton(
        alphabet=left.alphabet | right.alphabet,
        states=left.states | right.states,
        initial_states=left.initial_states | right.initial_states,
        accepting_states=left.accepting_states | right.accepting_states,
        transitions={**left.transitions, **right.transitions}
    )


def _empty_word_automaton(state: State = 'q0') -> FiniteAutomaton:
    """Returns the automaton with a unique state that is both initial and
    accepting.
    """
    return FiniteAutomaton(
        alphabet=set(),
        states={state},
        initial_states={state},
        accepting_states={state},
        transitions=dict()
    )


def _letter_automaton(
        letter: Letter,
        initial_state: State = 'q0',
        accepting_state: State = 'q1') -> FiniteAutomaton:
    """Returns a 2 states automaton that only accepts the given letter.

    The letter may be ε.
    """
    return FiniteAutomaton(
        alphabet={letter},
        states={initial_state, accepting_state},
        initial_states={initial_state},
        accepting_states={accepting_state},
        transitions={initial_state: [(letter, accepting_state)]}
    )


def thompson(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Transforms a regular expression into an equivalent automaton using
    Thompson's algorithm.
    """
    if regular_expression.node_type == 'CONCAT':
        return thompson_concat(regular_expression, alphabet, index)
    if regular_expression.node_type == 'EPSILON':
        return thompson_epsilon(index)
    if regular_expression.node_type == 'LETTER':
        return thompson_letter(regular_expression, index)
    if regular_expression.node_type == 'PLUS':
        return thompson_plus(regular_expression, alphabet, index)
    if regular_expression.node_type == 'STAR':
        return thompson_star(regular_expression, alphabet, index)
    raise ValueError(f'Unknown node type {regular_expression.node_type}')


def thompson_concat(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, CONCAT case
    """
    if not regular_expression.left:
        raise ValueError("This should not happen :/")
    if not regular_expression.right:
        raise ValueError("This should not happen :/")
    left = thompson(regular_expression.left, alphabet, index)
    index += len(left.states)
    right = thompson(regular_expression.right, alphabet, index)
    return _concatenation_automaton(left, right)


def thompson_epsilon(index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, EPSILON case
    """
    return _letter_automaton('ε', f'q{index}', f'q{index + 1}')


def thompson_letter(
        regular_expression: RegularExpression,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, LETTER case
    """
    if not regular_expression.letter:
        raise ValueError("This should not happen :/")
    return _letter_automaton(
        regular_expression.letter,
        f'q{index}',
        f'q{index + 1}'
    )


def thompson_plus(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, PLUS case
    """
    if not regular_expression.left:
        raise ValueError("This should not happen :/")
    if not regular_expression.right:
        raise ValueError("This should not happen :/")
    left = thompson(regular_expression.left, alphabet, index)
    index += len(left.states)
    right = thompson(regular_expression.right, alphabet, index)
    index += len(right.states)
    return _concatenation_automaton(
        _empty_word_automaton(f'q{index}'),
        _disjoint_union_automaton(left, right),
        _empty_word_automaton(f'q{index + 1}')
    )


def thompson_star(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, STAR case
    """
    if not regular_expression.inner:
        raise ValueError("This should not happen :/")
    inner = thompson(regular_expression.inner, alphabet, index)
    index += len(inner.states)
    q_init_inner = list(inner.initial_states)[0]
    q_acc_inner = list(inner.accepting_states)[0]
    q_init = f'q{index}'
    q_acc = f'q{index + 1}'
    result = _concatenation_automaton(
        _empty_word_automaton(q_init),
        inner,
        _empty_word_automaton(q_acc)
    )
    result.transitions[q_init].append(('ε', q_acc))
    result.transitions[q_acc_inner].append(('ε', q_init_inner))
    return result

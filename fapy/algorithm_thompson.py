"""Transforms a regular expression into an equivalent automaton using
Thompson's algorithm.
"""

from fapy.common import (
    Alphabet,
    Letter,
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton,
    empty_word_automaton,
    letter_automaton,
)
from fapy.regular_expression import (
    RegularExpression
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
    return left * right


def thompson_epsilon(index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, EPSILON case
    """
    return letter_automaton('ε', f'q{index}', f'q{index + 1}')


def thompson_letter(
        regular_expression: RegularExpression,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, LETTER case
    """
    if not regular_expression.letter:
        raise ValueError("This should not happen :/")
    return letter_automaton(
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
    return empty_word_automaton(f'q{index}') * (left + right) * \
        empty_word_automaton(f'q{index + 1}')


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
    result = empty_word_automaton(q_init) * inner * \
        empty_word_automaton(q_acc)
    result.transitions[q_init].append(('ε', q_acc))
    result.transitions[q_acc_inner].append(('ε', q_init_inner))
    return result

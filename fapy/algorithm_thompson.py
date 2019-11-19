"""Implementation of Thompson's algorithm

Transforms a regular expression into an equivalent finite automaton by
recursion on the abstract syntax tree of that regular expression, see
:class:`regular_expression.RegularExpression`.

See also:
    `Wikipedia page <https://en.wikipedia.org/wiki/Thompson%27s_construction>`_
"""

from fapy.common import (
    Alphabet,
)
from fapy.finite_automaton import (
    FiniteAutomaton,
    empty_word_automaton,
    letter_automaton,
)
from fapy.regular_expression import (
    RegularExpression
)


def _thompson_concat(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, ``CONCAT`` case
    """
    left = thompson(regular_expression.left, alphabet, index)
    index += len(left.states)
    right = thompson(regular_expression.right, alphabet, index)
    return left * right


def _thompson_epsilon(index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, ``EPSILON`` case
    """
    return letter_automaton('ε', f'q{index}', f'q{index + 1}')


def _thompson_letter(
        regular_expression: RegularExpression,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, ``LETTER`` case
    """
    return letter_automaton(
        regular_expression.letter,
        f'q{index}',
        f'q{index + 1}'
    )


def _thompson_plus(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, ``PLUS`` case
    """
    left = thompson(regular_expression.left, alphabet, index)
    index += len(left.states)
    right = thompson(regular_expression.right, alphabet, index)
    index += len(right.states)
    return empty_word_automaton(f'q{index}') * (left + right) * \
        empty_word_automaton(f'q{index + 1}')


def _thompson_star(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Thompson's algorithm, ``STAR`` case
    """
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


def thompson(
        regular_expression: RegularExpression,
        alphabet: Alphabet,
        index: int = 0) -> FiniteAutomaton:
    """Implementation of Thompson's algorithm

    Raises:
        NotImplementedError: If :attr:`RegularExpression.node_type` is
            invalid
    """
    if regular_expression.node_type == 'CONCAT':
        return _thompson_concat(regular_expression, alphabet, index)
    if regular_expression.node_type == 'EPSILON':
        return _thompson_epsilon(index)
    if regular_expression.node_type == 'LETTER':
        return _thompson_letter(regular_expression, index)
    if regular_expression.node_type == 'PLUS':
        return _thompson_plus(regular_expression, alphabet, index)
    if regular_expression.node_type == 'STAR':
        return _thompson_star(regular_expression, alphabet, index)
    raise NotImplementedError(
        f'Unknown node type {regular_expression.node_type}'
    )

"""Glushkov's algorithm
"""

from typing import (
    Set,
    Tuple
)


from fapy.algorithm_thompson import (
    _concatenation_automaton,
    _empty_word_automaton
)
from fapy.common import (
    Letter
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    RegularExpression
)


def _linearize_regular_expression(
        regular_expression: RegularExpression,
        index: int = 0) -> Tuple[RegularExpression, int]:
    """"Makes a regular expression linear by renaming all variables to unique
    names.
    """
    if regular_expression.node_type == 'CONCAT':
        left, index = _linearize_regular_expression(
            regular_expression.left,
            index
        )
        right, index = _linearize_regular_expression(
            regular_expression.right,
            index
        )
        return (RegularExpression('CONCAT', left=left, right=right), index)
    if regular_expression.node_type == 'EPSILON':
        return (RegularExpression('EPSILON'), index)
    if regular_expression.node_type == 'LETTER':
        return (
            RegularExpression(
                'LETTER',
                letter=str(regular_expression.letter) + str(index)
            ),
            index + 1
        )
    if regular_expression.node_type == 'PLUS':
        left, index = _linearize_regular_expression(
            regular_expression.left,
            index
        )
        right, index = _linearize_regular_expression(
            regular_expression.right,
            index
        )
        return (RegularExpression('PLUS', left=left, right=right), index)
    if regular_expression.node_type == 'STAR':
        inner, index = _linearize_regular_expression(
            regular_expression.inner,
            index
        )
        return (RegularExpression('STAR', inner=inner), index)
    raise ValueError(f'Unknown node type {regular_expression.node_type}')


def _accepting_letters(regular_expression: RegularExpression) -> Set[Letter]:
    if regular_expression.node_type == 'CONCAT':
        if regular_expression.right.accepts_epsilon():
            return _accepting_letters(regular_expression.left) | \
                _accepting_letters(regular_expression.right)
        return _accepting_letters(regular_expression.right)
    if regular_expression.node_type == 'EPSILON':
        return set()
    if regular_expression.node_type == 'LETTER':
        return {regular_expression.letter}
    if regular_expression.node_type == 'PLUS':
        return _accepting_letters(regular_expression.left) | \
            _accepting_letters(regular_expression.right)
    if regular_expression.node_type == 'STAR':
        return _accepting_letters(regular_expression.inner)
    raise ValueError(f'Unknown node type {regular_expression.node_type}')


def _initial_letters(regular_expression: RegularExpression) -> Set[Letter]:
    if regular_expression.node_type == 'CONCAT':
        if regular_expression.left.accepts_epsilon():
            return _initial_letters(regular_expression.left) | \
                _initial_letters(regular_expression.right)
        return _initial_letters(regular_expression.left)
    if regular_expression.node_type == 'EPSILON':
        return set()
    if regular_expression.node_type == 'LETTER':
        return {regular_expression.letter}
    if regular_expression.node_type == 'PLUS':
        return _initial_letters(regular_expression.left) | \
            _initial_letters(regular_expression.right)
    if regular_expression.node_type == 'STAR':
        return _initial_letters(regular_expression.inner)
    raise ValueError(f'Unknown node type {regular_expression.node_type}')


def _successors(
        regular_expression: RegularExpression,
        letter: Letter) -> Set[Letter]:
    """From a regular expression, returns all potential successors of a
    given letter.
    """
    if regular_expression.node_type == 'CONCAT':
        if letter in _accepting_letters(regular_expression.left):
            return _successors(regular_expression.left, letter) | \
                _successors(regular_expression.right, letter) | \
                _initial_letters(regular_expression.right)
        return _successors(regular_expression.left, letter) | \
            _successors(regular_expression.right, letter)
    if regular_expression.node_type == 'EPSILON':
        return set()
    if regular_expression.node_type == 'LETTER':
        return set()
    if regular_expression.node_type == 'PLUS':
        return _successors(regular_expression.left, letter) | \
            _successors(regular_expression.right, letter)
    if regular_expression.node_type == 'STAR':
        if letter in _accepting_letters(regular_expression.inner):
            return _successors(regular_expression.inner, letter) | \
                _initial_letters(regular_expression.inner)
        return _successors(regular_expression.inner, letter)
    raise ValueError(f'Unknown node type {regular_expression.node_type}')


def glushkov(regular_expression: RegularExpression) -> FiniteAutomaton:

    linearized, _ = _linearize_regular_expression(regular_expression)
    q_init_result = '0'
    result = FiniteAutomaton(
        alphabet=regular_expression.alphabet(),
        states=linearized.alphabet() | {q_init_result},
        initial_states={q_init_result},
        accepting_states=_accepting_letters(linearized),
        transitions={
            q_init_result: []
        }
    )

    for letter in _initial_letters(linearized):
        real_letter = letter[0]
        result.transitions[q_init_result].append((real_letter, letter))

    for letter in linearized.alphabet():
        if letter not in result.transitions:
            result.transitions[letter] = []
        for successor in _successors(linearized, letter):
            real_letter = successor[0]
            result.transitions[letter].append((real_letter, successor))

    if linearized.accepts_epsilon():
        result.accepting_states |= {q_init_result}

    return result
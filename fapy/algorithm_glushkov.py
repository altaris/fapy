"""Implementation of Glushvok's algorithm

See also:
    `Wikipedia page <https://en.wikipedia.org/wiki/Glushkov%27s_construction_algorithm>`_
"""

from typing import (
    Tuple
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
    """"Linearizes a regular expression by renaming all variables to unique
    names

    Example::

        re, _ = _linearize_regular_expression(
            parse_regular_expression('a a + b*')
        )
        print(str(re))

    prints ``a0 a1 + b2*``. The first number to be used can be specified with
    the optional ``index`` argument::

        re, _ = _linearize_regular_expression(
            parse_regular_expression('a a + b*', 4)
        )
        print(str(re))

    prints ``a4 a5 + b6*``

    Args:
        regular_expression: The :class:`regular_expression.RegularExpression`
            to linearize
        index: The starting index. Defaults to :math:`0`.

    Returns:
        A tuple formed by

        1. The linearized regular expression
        2. The next available index

    Raises:
        NotImplementedError: If :attr:`RegularExpression.node_type` is
            invalid
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

    raise NotImplementedError(f'Unknown node type {regular_expression.node_type}')


def glushkov(regular_expression: RegularExpression) -> FiniteAutomaton:
    """Implementation of Glushkov's algorithm
    """

    linearized, _ = _linearize_regular_expression(regular_expression)
    q_init_result = '0'
    result = FiniteAutomaton(
        alphabet=regular_expression.alphabet(),
        states=linearized.alphabet() | {q_init_result},
        initial_states={q_init_result},
        accepting_states=linearized.accepting_letters(),
        transitions={
            q_init_result: []
        }
    )

    for letter in linearized.initial_letters():
        real_letter = letter[0]
        result.transitions[q_init_result].append((real_letter, letter))

    for letter in linearized.alphabet():
        if letter not in result.transitions:
            result.transitions[letter] = []
        for successor in linearized.successors(letter):
            real_letter = successor[0]
            result.transitions[letter].append((real_letter, successor))

    if linearized.accepts_epsilon():
        result.accepting_states |= {q_init_result}

    return result
"""Residual computation

Given a langage :math:`\\mathcal{L}` over an alphabet :math:`\\Sigma`, and a
word :math:`w \\in \\Sigma^*`, the *residual* :math:`w^{-1} \\mathcal{L}` of
:math:`\\mathcal{L}` by :math:`w` is the langage :math:`\\{ u \\in \\Sigma^*
\\mid wu \\in \\mathcal{L} \\}`.

The main function of this module, :meth:`algorithm_residual.residual`, takes a
:class:`regular_expression.RegularExpression` intead of an actual set of words,
and returns a :class:`regular_expression.RegularExpression`.
"""

from typing import (
    Dict,
    List,
    Optional,
    Tuple
)

from fapy.common import (
    Letter,
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.regular_expression import (
    parse_regular_expression,
    RegularExpression
)


def _residual_concat(
        regular_expression: RegularExpression,
        letter: Letter) -> Optional[RegularExpression]:
    """Residual computation, ``CONCAT`` case
    """
    residual_left = residual(regular_expression.left, letter)
    residual_right = residual(regular_expression.right, letter)
    if regular_expression.left.accepts_epsilon():
        if residual_left is not None and residual_right is not None:
            return RegularExpression(
                'PLUS',
                left=RegularExpression(
                    'CONCAT',
                    left=residual_left,
                    right=regular_expression.right
                ),
                right=residual_right
            )
        if residual_left is not None:
            return RegularExpression(
                'CONCAT',
                left=residual_left,
                right=regular_expression.right
            )
        if residual_right is not None:
            return residual_right
        return None
    if residual_left is not None:
        return RegularExpression(
            'CONCAT',
            left=residual_left,
            right=regular_expression.right
        )
    return None


def _residual_letter(
        regular_expression: RegularExpression,
        letter: Letter) -> Optional[RegularExpression]:
    """Residual computation, ``LETTER`` case
    """
    if letter == regular_expression.letter:
        return RegularExpression('EPSILON')
    return None


def _residual_plus(
        regular_expression: RegularExpression,
        letter: Letter) -> Optional[RegularExpression]:
    """Residual computation, ``PLUS`` case
    """
    residual_left = residual(regular_expression.left, letter)
    residual_right = residual(regular_expression.right, letter)
    if residual_left is not None and residual_right is not None:
        return RegularExpression(
            'PLUS',
            left=residual_left,
            right=residual_right,
        )
    if residual_left is not None:
        return residual_left
    if residual_right is not None:
        return residual_right
    return None


def _residual_star(
        regular_expression: RegularExpression,
        letter: Letter) -> Optional[RegularExpression]:
    """Residual computation, ``STAR`` case
    """
    residual_inner = residual(regular_expression.inner, letter)
    if residual_inner is not None:
        return RegularExpression(
            'CONCAT',
            left=residual_inner,
            right=RegularExpression(
                'STAR',
                inner=regular_expression.inner
            )
        )
    return None


def _state_identifier(regular_expression: Optional[RegularExpression]) -> str:
    """Convenience function that provides a string representation of an
    ``Optional[regular_expression.RegularExpression]``
    """
    if regular_expression is None:
        return ''
    return str(regular_expression).replace(' ', '')


def residual(
        regular_expression: Optional[RegularExpression],
        word: str) -> Optional[RegularExpression]:
    """Returns the resitual regular expression, or ``None`` if the corresponding
    residual is empty

    Raises:
        NotImplementedError: If :attr:`RegularExpression.node_type` is
            invalid
    """

    if regular_expression is None:
        return None
    if not word:
        return regular_expression
    if len(word) > 1:
        return residual(residual(regular_expression, word[0]), word[1:])

    letter = word[0]

    if regular_expression.node_type == 'CONCAT':
        return _residual_concat(regular_expression, letter)
    if regular_expression.node_type == 'EPSILON':
        return None
    if regular_expression.node_type == 'LETTER':
        return _residual_letter(regular_expression, letter)
    if regular_expression.node_type == 'PLUS':
        return _residual_plus(regular_expression, letter)
    if regular_expression.node_type == 'STAR':
        return _residual_star(regular_expression, letter)
    raise NotImplementedError(
        f'Unknown node type {regular_expression.node_type}'
    )


def residual_automaton(
        regular_expression: RegularExpression) -> FiniteAutomaton:
    """From a regular expression, constructs an equivalent finite automaton
    using the residuals method
    """

    initial_state = _state_identifier(regular_expression)
    accepting_states = []
    alphabet = regular_expression.alphabet()
    transitions: Dict[State, List[Tuple[Letter, State]]] = {}
    unexplored_states = [initial_state]

    while unexplored_states:
        state = unexplored_states.pop(0)
        state_re = parse_regular_expression(state)
        if state_re.accepts_epsilon():
            accepting_states.append(state)
        transitions[state] = []
        for letter in alphabet:
            next_residual = residual(state_re, letter)
            next_state = _state_identifier(next_residual)
            if next_residual is not None:
                transitions[state].append((letter, next_state))
                # Equivalent re can have different string representations...
                if next_state not in transitions:
                    transitions[next_state] = []
                    unexplored_states.append(next_state)

    return FiniteAutomaton(
        alphabet=alphabet,
        states=set(transitions.keys()),
        initial_states={initial_state},
        accepting_states=set(accepting_states),
        transitions=transitions
    )

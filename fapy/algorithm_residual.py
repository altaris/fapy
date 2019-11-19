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
    Optional,
)

from fapy.common import (
    Letter
)
from fapy.regular_expression import (
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

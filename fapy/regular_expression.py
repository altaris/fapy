"""This module implements a lexer, parser, and a representation of regular
expressions

A regular expression over an alphabet :math:`A` is either:

* :math:`\\epsilon`;
* a letter :math:`a \\in A`;
* (*concatenation*) an expression :math:`r r'`, where :math:`r` and :math:`r'`
  are regular expressions;
* (*sum*) an expression :math:`r + r'`, where :math:`r` and :math:`r'` are
  regular expressions;
* (*Kleene's star*) an expression :math:`r^*`, where :math:`r` is a regular
  expression.

Star binds stringer than concatenation, which itself binds stronger than sums.

Here is a usage example::

    regular_expression = parse_regular_expression('(a + b)* a (a + b)*')

This regular expression accepts all words containing the letter :math:`a`.

Warning:
    Due to a limitation of the current lexer, concatenation binds weaker than
    sums, although it should be the other way around.
"""

from copy import (
    deepcopy
)
from typing import (
    Optional,
    Set
)


from purplex import (
    attach,
    LEFT,
    Lexer,
    Parser,
    TokenDef
)


from fapy.common import (
    Alphabet,
    Letter
)


class RegularExpression:
    """Representation of regular expression my means of abstract syntax trees

    To construct a :class:`RegularExpression`, use
    :meth:`parse_regular_expression`.

    Abstract syntax tree (AST) node types:

    * ``CONCAT``: concatenation of the :attr:`RegularExpression._left` and
      :attr:`RegularExpression._right` regular expressions;
    * ``EPSILON``: the :math:`\\epsilon` regular expression;
    * ``LETTER``: a regular expression matching letter
      :attr:`RegularExpression._letter`;
    * ``PLUS``: sum of the :attr:`RegularExpression._left` and
      :attr:`RegularExpression._right` regular expressions;
    * ``STAR``: star of the :attr:`RegularExpression._inner` regular
      expression.
    """

    NODE_TYPES = (
        'CONCAT',
        'EPSILON',
        'LETTER',
        'PLUS',
        'STAR',
    )

    node_type: str
    """The node type, among ``CONCAT``, ``EPSILON``, ``LETTER``, ``PLUS``,
    ``STAR``"""
    _left = None  # type: Optional[RegularExpression]
    """Left node, if applicable"""
    _letter = None  # type: Optional[Letter]
    """Letter of the node, if applicable"""
    _right = None  # type: Optional[RegularExpression]
    """Right node, if applicable"""
    _inner = None  # type: Optional[RegularExpression]
    """Inner node, if applicable"""

    def __init__(self, node_type: str, **kwargs):
        """Constructor

        To construct a :class:`RegularExpression`, use
        :meth:`parse_regular_expression`.

        Args:
            node_type: The type of the node, among ``CONCAT``, ``EPSILON``,
            ``LETTER``, ``PLUS``, ``STAR``

        Keyword Args:
           inner: Inner node, if applicable
           left: Left node, if applicable
           letter: Letter of the node, if applicable
           right: Right node, if applicable
        """
        self.node_type = node_type
        if node_type == 'CONCAT':
            self._init_left_right(**kwargs)
            if self.left.node_type == 'EPSILON' and \
                self.right.node_type == 'EPSILON':
                self.node_type = 'EPSILON'
                self._left = None
                self._right = None
            elif self.left.node_type == 'EPSILON':
                right = deepcopy(self.right)
                self.node_type = right.node_type
                self._left = right._left
                self._letter = right._letter
                self._right = right._right
                self._inner = right._inner
            elif self.right.node_type == 'EPSILON':
                left = deepcopy(self.left)
                self.node_type = left.node_type
                self._left = left._left
                self._letter = left._letter
                self._right = left._right
                self._inner = left._inner
        elif node_type == 'EPSILON':
            pass
        elif node_type == 'LETTER':
            if not kwargs.get('letter'):
                raise ValueError(f'Node type {node_type} expects letter')
            self._letter = kwargs.get('letter')
        elif node_type == 'PLUS':
            self._init_left_right(**kwargs)
        elif node_type == 'STAR':
            self._init_inner(**kwargs)
            if self.inner.node_type == 'EPSILON':
                self.node_type = 'EPSILON'
                self._inner = None
        else:
            raise NotImplementedError(f'Unknown node type {node_type}')

    def __repr__(self) -> str:
        """Provides a string representation of the regular expression

        For instance the regular expression `(a + ε) b*` is represented as
        `CONCAT(PLUS(a, ε), STAR(b))`.

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type == 'CONCAT':
            return 'CONCAT(' + repr(self.left) + ', ' + repr(self.right) + ')'
        if self.node_type == 'EPSILON':
            return 'ε'
        if self.node_type == 'LETTER':
            return str(self.letter)
        if self.node_type == 'PLUS':
            return 'PLUS(' + repr(self.left) + ', ' + repr(self.right) + ')'
        if self.node_type == 'STAR':
            return 'STAR(' + repr(self.inner) + ')'
        raise NotImplementedError(f'Unknown node type {self.node_type}')

    def __str__(self) -> str:
        """Provides a human-friendly string representation of the regular
        expression

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type == 'CONCAT':
            left_str = str(self.left)
            right_str = str(self.right)
            if self.left.node_type == 'PLUS':
                left_str = '(' + left_str +')'
            if self.right.node_type == 'PLUS':
                right_str = '(' + right_str +')'
            return left_str + ' ' + right_str
        if self.node_type == 'EPSILON':
            return 'ε'
        if self.node_type == 'LETTER':
            return str(self.letter)
        if self.node_type == 'PLUS':
            return str(self.left) + ' + ' + str(self.right)
        if self.node_type == 'STAR':
            return '(' + str(self.inner) + ')*'
        raise NotImplementedError(f'Unknown node type {self.node_type}')

    def _init_inner(self, **kwargs) -> None:
        """Inits the node with an inner AST

        Convenience method for :meth:`RegularExpression.__init__`.

        Raises:
            ValueError: If ``kwargs`` does not contain key ``inner``
        """
        if not kwargs.get('inner'):
            raise ValueError(f'Node type {self.node_type} expects inner ast')
        self._inner = kwargs.get('inner')

    def _init_left_right(self, **kwargs) -> None:
        """Inits the node with an left and right AST

        Convenience method for :meth:`RegularExpression.__init__`.

        Raises:
            ValueError: If ``kwargs`` does not contain key ``left`` or
            ``right``
        """
        if not kwargs.get('left'):
            raise ValueError(f'Node type {self.node_type} expects left ast')
        if not kwargs.get('right'):
            raise ValueError(f'Node type {self.node_type} expects left ast')
        self._left = kwargs.get('left')
        self._right = kwargs.get('right')

    def accepting_letters(self) -> Set[Letter]:
        """Returns the accepting letters of the regular expression

        A letter is *accepting* if there exist a word accepted by the regular
        expression finishing with that letter. For example, the accepting
        letters of :math:`(a + bc)^*` are :math:`a` and :math:`c`, but not
        :math:`b`.

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type == 'CONCAT':
            if self.right.accepts_epsilon():
                return self.left.accepting_letters() | \
                    self.right.accepting_letters()
            return self.right.accepting_letters()
        if self.node_type == 'EPSILON':
            return set()
        if self.node_type == 'LETTER':
            return {self.letter}
        if self.node_type == 'PLUS':
            return self.left.accepting_letters() | \
                self.right.accepting_letters()
        if self.node_type == 'STAR':
            return self.inner.accepting_letters()
        raise NotImplementedError(f'Unknown node type {self.node_type}')

    def accepts_epsilon(self) -> bool:
        """Returns whether the regular expression accepts the empty word

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type == 'CONCAT':
            return self.left.accepts_epsilon() and self.right.accepts_epsilon()
        if self.node_type == 'EPSILON':
            return True
        if self.node_type == 'LETTER':
            return False
        if self.node_type == 'PLUS':
            return self.left.accepts_epsilon() or self.right.accepts_epsilon()
        if self.node_type == 'STAR':
            return True
        raise NotImplementedError(f'Unknown node type {self.node_type}')

    def alphabet(self) -> Alphabet:
        """Returns the alphabet of the regular expression

        The alphabet of a regular expression is the set of all letters
        appearing in it. For example, the alphabet of :math:`ac + c^*` is
        :math:`\\{ a, c \\}`.

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type in ['CONCAT', 'PLUS']:
            return self.left.alphabet() | self.right.alphabet()
        if self.node_type == 'EPSILON':
            return set()
        if self.node_type == 'LETTER':
            return {self.letter}
        if self.node_type == 'STAR':
            return self.inner.alphabet()
        raise NotImplementedError(f'Unknown node type {self.node_type}')

    def initial_letters(self) -> Set[Letter]:
        """Returns the initial letters of the regular expression

        A letter is *initial* if there exist a word accepted by the regular
        expression starting with that letter. For example, the initial letters
        of :math:`(a + bc)^*` are :math:`a` and :math:`b`, but not :math:`c`.

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type == 'CONCAT':
            if self.left.accepts_epsilon():
                return self.left.initial_letters() | \
                    self.right.initial_letters()
            return self.left.initial_letters()
        if self.node_type == 'EPSILON':
            return set()
        if self.node_type == 'LETTER':
            return {self.letter}
        if self.node_type == 'PLUS':
            return self.left.initial_letters() | \
                self.right.initial_letters()
        if self.node_type == 'STAR':
            return self.inner.initial_letters()
        raise NotImplementedError(f'Unknown node type {self.node_type}')

    @property
    def inner(self) -> 'RegularExpression':
        """Asserts that :attr:`RegularExpression._inner` is not ``None``, and
        returns it

        Convenience function to product code that type-checks.

        Raises:
            ValueError: If :attr:`RegularExpression._inner` is ``None``
        """
        if not self._inner:
            raise ValueError('Value of member "inner" is None')
        return self._inner

    @property
    def left(self) -> 'RegularExpression':
        """Asserts that :attr:`RegularExpression._left` is not ``None``, and
        returns it

        Convenience function to product code that type-checks.

        Raises:
            ValueError: If :attr:`RegularExpression._left` is ``None``
        """
        if not self._left:
            raise ValueError('Value of member "left" is None')
        return self._left

    @property
    def letter(self) -> Letter:
        """Asserts that :attr:`RegularExpression._letter` is not ``None``, and
        returns it

        Convenience function to product code that type-checks.

        Raises:
            ValueError: If :attr:`RegularExpression._letter` is ``None``
        """
        if not self._letter:
            raise ValueError('Value of member "letter" is None')
        return self._letter

    @property
    def right(self) -> 'RegularExpression':
        """Asserts that :attr:`RegularExpression._right` is not ``None``, and
        returns it

        Convenience function to product code that type-checks.

        Raises:
            ValueError: If :attr:`RegularExpression._right` is ``None``
        """
        if not self._right:
            raise ValueError('Value of member "right" is None')
        return self._right

    def successors(self, letter: Letter) -> Set[Letter]:
        """Returns all potential successors of a given letter

        For instance, in :math:`(a + bc)^*`, the successor set of :math:`a` is
        :math:`\\{ b \\}`, the successor set of :math:`b` is :math:`\\{ c \\}`,
        and the successor set of :math:`c` is :math:`\\{ a, b \\}`.

        Raises:
            NotImplementedError: If :attr:`RegularExpression.node_type` is
                invalid
        """
        if self.node_type == 'CONCAT':
            if letter in self.left.accepting_letters():
                return self.left.successors(letter) | \
                    self.right.successors(letter) | \
                    self.right.initial_letters()
            return self.left.successors(letter) | self.right.successors(letter)
        if self.node_type == 'EPSILON':
            return set()
        if self.node_type == 'LETTER':
            return set()
        if self.node_type == 'PLUS':
            return self.left.successors(letter) | self.right.successors(letter)
        if self.node_type == 'STAR':
            if letter in self.inner.accepting_letters():
                return self.inner.successors(letter) | \
                    self.inner.initial_letters()
            return self.inner.successors(letter)
        raise NotImplementedError(f'Unknown node type {self.node_type}')


class ReLexer(Lexer):
    """Regular expression lexer

    See also:
        `Purplex homepage <https://github.com/mtomwing/purplex>`_
    """

    EPSILON = TokenDef(r'ε')
    LETTER = TokenDef(r'\w')
    LPAREN = TokenDef(r'\(')
    PLUS = TokenDef(r'\+')
    RPAREN = TokenDef(r'\)')
    STAR = TokenDef(r'\*')
    WHITESPACE = TokenDef(r'[\s\n]+', ignore=True)


# pylint: disable=missing-function-docstring
# pylint: disable=unused-argument
class ReParser(Parser):
    """Regular expression parser

    See also:
        `Purplex homepage <https://github.com/mtomwing/purplex>`_
    """

    LEXER = ReLexer
    START = 'e'

    PRECEDENCE = (
        (LEFT, 'STAR'),
        (LEFT, 'PLUS')
    )

    @attach('e : EPSILON')
    def epsilon(self, epsilon):
        return RegularExpression('EPSILON')

    @attach('e : LETTER')
    def letter(self, letter):
        return RegularExpression('LETTER', letter=letter)

    @attach('e : LPAREN e RPAREN')
    def parens(self, lparen, inner, rparen):
        return inner

    @attach('e : e PLUS e')
    def addition(self, left, plus, right):
        return RegularExpression('PLUS', left=left, right=right)

    @attach('e : e STAR')
    def star(self, inner, star):
        if inner.node_type == 'STAR':
            return RegularExpression('STAR', inner=inner.inner)
        else:
            return RegularExpression('STAR', inner=inner)

    @attach('e : e e')
    def concat(self, left, right):
        if left.node_type == 'EPSILON':
            return right
        if right.node_type == 'EPSILON':
            return left
        return RegularExpression('CONCAT', left=left, right=right)


def parse_regular_expression(string: str) -> RegularExpression:
    """Parses a regular expression, returning a `RegularExpression` object
    """
    return ReParser().parse(string)

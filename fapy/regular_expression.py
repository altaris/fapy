"""Regular expressions
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


# pylint: disable=unused-import
from fapy.common import (
    Alphabet,
    Letter
)


class RegularExpression:
    """Regular expression abstract syntax tree
    """

    NODE_TYPES = (
        'CONCAT',
        'EPSILON',
        'LETTER',
        'PLUS',
        'STAR',
    )

    node_type: str
    _left = None  # type: Optional[RegularExpression]
    _letter = None  # type: Optional[Letter]
    _right = None  # type: Optional[RegularExpression]
    _inner = None  # type: Optional[RegularExpression]

    def __init__(self, node_type: str, **kwargs):
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
        """Inits the node with an inner ast (for e.g. STAR)
        """
        if not kwargs.get('inner'):
            raise ValueError(f'Node type {self.node_type} expects inner ast')
        self._inner = kwargs.get('inner')

    def _init_left_right(self, **kwargs) -> None:
        """Inits the node with a left and right ast (for e.g. CONCAT)
        """
        if not kwargs.get('left'):
            raise ValueError(f'Node type {self.node_type} expects left ast')
        if not kwargs.get('right'):
            raise ValueError(f'Node type {self.node_type} expects left ast')
        self._left = kwargs.get('left')
        self._right = kwargs.get('right')

    def accepting_letters(self) -> Set[Letter]:
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
        """Returns whether the regular expression accepts the empty word"""
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
    def left(self) -> 'RegularExpression':
        """Asserts that left is not None, and returns it
        """
        if not self._left:
            raise ValueError('Value of member "left" is None')
        return self._left

    @property
    def letter(self) -> Letter:
        """Asserts that letter is not None, and returns it
        """
        if not self._letter:
            raise ValueError('Value of member "letter" is None')
        return self._letter

    def successors(self, letter: Letter) -> Set[Letter]:
        """From a regular expression, returns all potential successors of a
        given letter.
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

    @property
    def right(self) -> 'RegularExpression':
        """Asserts that right is not None, and returns it
        """
        if not self._right:
            raise ValueError('Value of member "right" is None')
        return self._right

    @property
    def inner(self) -> 'RegularExpression':
        """Asserts that inner is not None, and returns it
        """
        if not self._inner:
            raise ValueError('Value of member "inner" is None')
        return self._inner


class ReLexer(Lexer):
    """Regular expression lexer
    """

    EPSILON = TokenDef(r'ε')
    LETTER = TokenDef(r'\w')
    LPAREN = TokenDef(r'\(')
    PLUS = TokenDef(r'\+')
    RPAREN = TokenDef(r'\)')
    STAR = TokenDef(r'\*')
    WHITESPACE = TokenDef(r'[\s\n]+', ignore=True)


class ReParser(Parser):
    """Regular expression parser
    """

    LEXER = ReLexer
    START = 'e'

    PRECEDENCE = (
        (LEFT, 'STAR'),
        (LEFT, 'PLUS')
    )

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @attach('e : EPSILON')
    def epsilon(self, epsilon):
        return RegularExpression('EPSILON')

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @attach('e : LETTER')
    def letter(self, letter):
        return RegularExpression('LETTER', letter=letter)

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @attach('e : LPAREN e RPAREN')
    def parens(self, lparen, inner, rparen):
        return inner

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @attach('e : e PLUS e')
    def addition(self, left, plus, right):
        return RegularExpression('PLUS', left=left, right=right)

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @attach('e : e STAR')
    def star(self, inner, star):
        if inner.node_type == 'STAR':
            return RegularExpression('STAR', inner=inner.inner)
        else:
            return RegularExpression('STAR', inner=inner)

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @attach('e : e e')
    def concat(self, left, right):
        if left.node_type == 'EPSILON':
            return right
        if right.node_type == 'EPSILON':
            return left
        return RegularExpression('CONCAT', left=left, right=right)


def parse_regular_expression(string: str) -> RegularExpression:
    """Parses a regular expression, returning an abstract syntax tree.
    """
    return ReParser().parse(string)

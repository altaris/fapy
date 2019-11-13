"""Regular expressions
"""

from typing import (
    Optional
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
    left = None  # type: Optional[RegularExpression]
    letter = None  # type: Optional[Letter]
    right = None  # type: Optional[RegularExpression]
    inner = None  # type: Optional[RegularExpression]

    def __init__(self, node_type: str, **kwargs):
        self.node_type = node_type
        if node_type == 'CONCAT':
            self.init_left_right(**kwargs)
        elif node_type == 'EPSILON':
            pass
        elif node_type == 'LETTER':
            if not kwargs.get('letter'):
                raise ValueError(f'Node type {node_type} expects letter')
            self.letter = kwargs.get('letter')
        elif node_type == 'PLUS':
            self.init_left_right(**kwargs)
        elif node_type == 'STAR':
            self.init_inner(**kwargs)
        else:
            raise ValueError(f'Unknown node type {node_type}')

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
        raise ValueError(f'Unknown node type {self.node_type}')

    def accepts_epsilon(self) -> bool:
        """Returns whether the regular expression accepts the empty word"""
        if self.node_type == 'CONCAT':
            if not self.left:
                raise ValueError("This should not happen :/")
            if not self.right:
                raise ValueError("This should not happen :/")
            return self.left.accepts_epsilon() and self.right.accepts_epsilon()
        if self.node_type == 'EPSILON':
            return True
        if self.node_type == 'LETTER':
            return False
        if self.node_type == 'PLUS':
            if not self.left:
                raise ValueError("This should not happen :/")
            if not self.right:
                raise ValueError("This should not happen :/")
            return self.left.accepts_epsilon() or self.right.accepts_epsilon()
        if self.node_type == 'STAR':
            return True
        raise ValueError(f'Unknown node type {self.node_type}')

    def alphabet(self) -> Alphabet:
        """Returns the alphabet of the regular expression
        """
        if self.node_type in ['CONCAT', 'PLUS']:
            if not self.left:
                raise ValueError("This should not happen :/")
            if not self.right:
                raise ValueError("This should not happen :/")
            return self.left.alphabet() | self.right.alphabet()
        if self.node_type == 'EPSILON':
            return set()
        if self.node_type == 'LETTER':
            if not self.letter:
                raise ValueError("This should not happen :/")
            return {self.letter}
        if self.node_type == 'STAR':
            if not self.inner:
                raise ValueError("This should not happen :/")
            return self.inner.alphabet()
        raise ValueError(f'Unknown node type {self.node_type}')

    def init_inner(self, **kwargs) -> None:
        """Inits the node with an inner ast (for e.g. STAR)
        """
        if not kwargs.get('inner'):
            raise ValueError(f'Node type {self.node_type} expects inner ast')
        self.inner = kwargs.get('inner')

    def init_left_right(self, **kwargs) -> None:
        """Inits the node with a left and right ast (for e.g. CONCAT)
        """
        if not kwargs.get('left'):
            raise ValueError(f'Node type {self.node_type} expects left ast')
        if not kwargs.get('right'):
            raise ValueError(f'Node type {self.node_type} expects left ast')
        self.left = kwargs.get('left')
        self.right = kwargs.get('right')



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

"""Unit tests
"""

import unittest

# pylint: disable wrong-import-position
from fapy.algorithm_residual import (
    residual
)
from fapy.regular_expression import (
    parse_regular_expression
)

class ResidualTest(unittest.TestCase):

    def test_residual(self):

        self.assertIsNone(residual(None, ''))
        self.assertIsNone(residual(None, 'a'))

        self.assertEqual(
            str(residual(parse_regular_expression('a'), 'a')),
            'ε'
        )
        self.assertIsNone(residual(parse_regular_expression('a'), 'b'))

        self.assertEqual(
            str(residual(parse_regular_expression('a b'), 'a')),
            'b'
        )
        self.assertIsNone(
            residual(parse_regular_expression('a b'), 'b')
        )

        self.assertEqual(
            str(residual(parse_regular_expression('a + b'), 'a')),
            'ε'
        )
        self.assertEqual(
            str(residual(parse_regular_expression('a + b'), 'b')),
            'ε'
        )

        self.assertEqual(
            str(residual(parse_regular_expression('(a + b) c'), 'a')),
            'c'
        )
        self.assertEqual(
            str(residual(parse_regular_expression('(a + b) c'), 'b')),
            'c'
        )
        self.assertIsNone(
            residual(parse_regular_expression('(a + b) c'), 'c')
        )

        self.assertEqual(
            str(
                residual(parse_regular_expression('((aa) + (bb)) cc'), 'a')
            ).replace(' ', ''),
            'acc'
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('((aa) + (bb)) cc'), 'b')
            ).replace(' ', ''),
            'bcc'
        )
        self.assertIsNone(
            residual(parse_regular_expression('((aa) + (bb)) cc'), 'c')
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('((aa) + (ab)) cc'), 'a')
            ).replace(' ', ''),
            '(a+b)cc'
        )

        self.assertEqual(
            str(
                residual(parse_regular_expression('(a + b)* a'), 'a')
            ).replace(' ', ''),
            '(a + b)* a + ε'.replace(' ', '')
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('(a + b)* a'), 'b')
            ).replace(' ', ''),
            '(a + b)* a'.replace(' ', '')
        )
        self.assertIsNone(
            residual(parse_regular_expression('(a + b)* a'), 'c')
        )

        self.assertEqual(
            str(
                residual(parse_regular_expression('(abc)* a'), 'a')
            ).replace(' ', ''),
            'b c (abc)* a + ε'.replace(' ', '')
        )

        self.assertEqual(
            str(
                residual(parse_regular_expression('(abc)* a'), 'ab')
            ).replace(' ', ''),
            'c (abc)* a'.replace(' ', '')
        )

        self.assertEqual(
            str(
                residual(parse_regular_expression('(a+ε)(b+ε)(c+ε)(d+ε)'), 'a')
            ).replace(' ', ''),
            '(b + ε)(c + ε)(d + ε)'.replace(' ', '')
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('(a+ε)(b+ε)(c+ε)(d+ε)'), 'b')
            ).replace(' ', ''),
            '(c + ε)(d + ε)'.replace(' ', '')
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('(a+ε)(b+ε)(c+ε)(d+ε)'), 'c')
            ).replace(' ', ''),
            'd + ε'.replace(' ', '')
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('(a+ε)(b+ε)(c+ε)(d+ε)'), 'ab')
            ).replace(' ', ''),
            '(c + ε) (d + ε)'.replace(' ', '')
        )

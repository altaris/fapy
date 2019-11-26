# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

"""Unit tests
"""

import unittest

# pylint: disable wrong-import-position
from fapy.algorithm_residual import (
    residual,
    residual_automaton
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
                residual(parse_regular_expression('(aa + bb) cc'), 'a')
            ).replace(' ', ''),
            'acc'
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('(aa + bb) cc'), 'b')
            ).replace(' ', ''),
            'bcc'
        )
        self.assertIsNone(
            residual(parse_regular_expression('(aa + bb) cc'), 'c')
        )
        self.assertEqual(
            str(
                residual(parse_regular_expression('(aa + ab) cc'), 'a')
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

    def test_residual_automaton(self):
        automaton1 = residual_automaton(parse_regular_expression('a'))
        automaton1.draw(
            name='ResidualTest.test_residual_automaton.automaton1'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton1.read('a'))
        self.assertFalse(automaton1.read(''))
        self.assertFalse(automaton1.read('aa'))
        self.assertFalse(automaton1.read('b'))
        self.assertFalse(automaton1.read('ab'))

        automaton2 = residual_automaton(parse_regular_expression('ab'))
        automaton2.draw(
            name='ResidualTest.test_residual_automaton.automaton2'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton2.read('ab'))
        self.assertFalse(automaton2.read(''))
        self.assertFalse(automaton2.read('a'))
        self.assertFalse(automaton2.read('aa'))
        self.assertFalse(automaton2.read('b'))
        self.assertFalse(automaton2.read('aba'))

        automaton3 = residual_automaton(parse_regular_expression('a*'))
        automaton3.draw(
            name='ResidualTest.test_residual_automaton.automaton3'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton3.read(''))
        self.assertTrue(automaton3.read('a'))
        self.assertTrue(automaton3.read('aa'))
        self.assertTrue(automaton3.read('aaa'))
        self.assertFalse(automaton3.read('b'))
        self.assertFalse(automaton3.read('aaaab'))

        automaton4 = residual_automaton(parse_regular_expression('a + b'))
        automaton4.draw(
            name='ResidualTest.test_residual_automaton.automaton4'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton4.read('a'))
        self.assertTrue(automaton4.read('b'))
        self.assertFalse(automaton4.read(''))
        self.assertFalse(automaton4.read('ab'))
        self.assertFalse(automaton4.read('ba'))

        automaton5 = residual_automaton(parse_regular_expression('(ab + c)* d'))
        automaton5.draw(
            name='ResidualTest.test_residual_automaton.automaton5'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton5.read('d'))
        self.assertTrue(automaton5.read('abd'))
        self.assertTrue(automaton5.read('cd'))
        self.assertTrue(automaton5.read('abcd'))
        self.assertTrue(automaton5.read('ababd'))
        self.assertFalse(automaton5.read(''))
        self.assertFalse(automaton5.read('ab'))
        self.assertFalse(automaton5.read('ad'))
        self.assertFalse(automaton5.read('abad'))

        automaton6 = residual_automaton(parse_regular_expression('(a b b*)*'))
        automaton6.draw(
            name='ResidualTest.test_residual_automaton.automaton6'
        ).render(directory='out/', format='pdf')
        self.assertTrue(automaton6.read(''))
        self.assertTrue(automaton6.read('ab'))
        self.assertTrue(automaton6.read('abb'))
        self.assertTrue(automaton6.read('abab'))
        self.assertTrue(automaton6.read('abbab'))
        self.assertFalse(automaton6.read('a'))
        self.assertFalse(automaton6.read('b'))
        self.assertFalse(automaton6.read('c'))
        self.assertFalse(automaton6.read('abababababaabababab'))

        # automaton7 = residual_automaton(parse_regular_expression('(a a* b*)*'))
        # automaton7.draw(
        #     name='ResidualTest.test_residual_automaton.automaton7'
        # ).render(directory='out/', format='pdf')
        # self.assertTrue(automaton7.read(''))
        # self.assertTrue(automaton7.read('a'))
        # self.assertTrue(automaton7.read('ab'))
        # self.assertTrue(automaton7.read('abb'))
        # self.assertTrue(automaton7.read('abab'))
        # self.assertFalse(automaton7.read('b'))
        # self.assertFalse(automaton7.read('abb'))

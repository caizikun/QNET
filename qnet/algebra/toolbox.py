# This file is part of QNET.
#
#    QNET is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#    QNET is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QNET.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012-2017, QNET authors (see AUTHORS file)
#
###########################################################################

"""Collection of tools to manually manipulate algebraic expressions"""

from functools import partial
from collections import OrderedDict

from .abstract_algebra import simplify
from .operator_algebra import Operator, Commutator, OperatorTimes
from .pattern_matching import pattern, wc

__all__ = ['expand_commutators_leibniz', 'evaluate_commutators']

__private__ = []  # anything not in __all__ must be in __private__


def expand_commutators_leibniz(expr, expand_expr=True):
    """Recursively expand commutators in `expr` according to the Leibniz rule.

    .. math::

        [A B, C] = A [B, C] + [A, C] B

    .. math::

        [A, B C] = [A, B] C + B [A, C]

    If `expand_expr` is True, expand products of sums in `expr`, as well as in
    the result.
    """
    recurse = partial(expand_commutators_leibniz, expand_expr=expand_expr)
    A = wc('A', head=Operator)
    C = wc('C', head=Operator)
    AB = wc('AB', head=OperatorTimes)
    BC = wc('BC', head=OperatorTimes)

    def leibniz_right(A, BC):
        """[A, BC] -> [A, B] C + B [A, C]"""
        B = BC.operands[0]
        C = OperatorTimes(*BC.operands[1:])
        return Commutator.create(A, B) * C + B * Commutator.create(A, C)

    def leibniz_left(AB, C):
        """[AB, C] -> A [B, C] C + [A, C] B"""
        A = AB.operands[0]
        B = OperatorTimes(*AB.operands[1:])
        return A * Commutator.create(B, C) + Commutator.create(A, C) * B

    rules = OrderedDict([
        ('leibniz1', (
            pattern(Commutator, A, BC),
            lambda A, BC: recurse(leibniz_right(A, BC).expand()))),
        ('leibniz2', (
            pattern(Commutator, AB, C),
            lambda AB, C: recurse(leibniz_left(AB, C).expand())))])

    if expand_expr:
        res = simplify(expr.expand(), rules).expand()
    else:
        res = simplify(expr, rules)
    return res


def evaluate_commutators(expr):
    """Evaluate all commutators in `expr`.

    All commutators are evaluated as the explicit formula

    .. math::

        [A, B] = A B - B A

    """
    A = wc('A', head=Operator)
    B = wc('B', head=Operator)
    return simplify(
        expr, [(pattern(Commutator, A, B), lambda A, B: A*B - B*A)])

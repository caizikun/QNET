#    This file is part of QNET.
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
"""Provides printers for a full-structured representation"""

from textwrap import dedent, indent

from sympy.printing.repr import (
    ReprPrinter as SympyReprPrinter, srepr as sympy_srepr)
from sympy.core.basic import Basic as SympyBasic

from .base import QnetBasePrinter
from ._render_head_repr import render_head_repr
from ..algebra.abstract_algebra import Expression
from ..algebra.singleton import Singleton

__all__ = ['QnetSReprPrinter', 'IndentedSReprPrinter']


class QnetSReprPrinter(QnetBasePrinter):
    """Printer for a string (ASCII) representation."""

    sympy_printer_cls = SympyReprPrinter

    def _render_str(self, string):
        return repr(string)

    def emptyPrinter(self, expr):
        """Fallback printer"""
        return render_head_repr(expr, sub_render=self.doprint)

    def _print_ndarray(self, expr):
        if len(expr.shape) == 2:
            rows = []
            for row in expr:
                rows.append(
                    '[' + ", ".join([self.doprint(val) for val in row]) + ']')
            return ("array([" + ", ".join(rows) +
                    "], dtype=%s)" % str(expr.dtype))
        else:
            raise ValueError("Cannot render %s" % expr)


class IndentedSympyReprPrinter(SympyReprPrinter):
    """Indented repr printer for Sympy objects"""

    def doprint(self, expr):
        res = super().doprint(expr)
        return "    " * (self._print_level - 1) + res


class IndentedSReprPrinter(QnetBasePrinter):
    """Printer for rendering an expression in such a way that the resulting
    string can be evaluated in an appropriate context to re-instantiate an
    identical object, using nested indentation (implementing
    ``srepr(expr, indented=True)``
    """

    sympy_printer_cls = IndentedSympyReprPrinter

    def _get_from_cache(self, expr):
        """Obtain cached result, prepend with the keyname if necessary, and
        indent for the current level"""
        is_cached, res = super()._get_from_cache(expr)
        if is_cached:
            indent_str = "    " * self._print_level
            return True, indent(res, indent_str)
        else:
            return False,  None

    def _write_to_cache(self, expr, res):
        """Store the cached result without indentation, and without the
        keyname"""
        res = dedent(res)
        super()._write_to_cache(expr, res)

    def _render_str(self, string):
        return "    " * self._print_level + repr(string)

    def emptyPrinter(self, expr):
        """Fallback printer"""
        indent_str = "    " * (self._print_level - 1)
        lines = []
        if isinstance(expr.__class__, Singleton):
            # We exploit that Singletons override __expr__ to directly return
            # their name
            return indent_str + repr(expr)
        if isinstance(expr, Expression):
            args = expr.args
            keys = expr.minimal_kwargs.keys()
            lines.append(indent_str + expr.__class__.__name__ + "(")
            for arg in args:
                lines.append(self.doprint(arg) + ",")
            for key in keys:
                arg = expr.kwargs[key]
                lines.append(
                    ("    " * self._print_level) + key + '=' +
                    self.doprint(arg).lstrip() + ",")
            if len(args) > 0 or len(keys) > 0:
                lines[-1] = lines[-1][:-1]  # drop trailing comma for last arg
            lines[-1] += ")"
        elif isinstance(expr, SympyBasic):
            lines.append(indent_str + sympy_srepr(expr))
        else:
            lines.append(indent_str + repr(expr))
        return "\n".join(lines)

    def _print_ndarray(self, expr):
        indent_str = "    " * (self._print_level - 1)
        if len(expr.shape) == 2:
            lines = [indent_str + "array([", ]
            self._print_level += 1
            for row in expr:
                indent_str = "    " * (self._print_level - 1)
                lines.append(indent_str + '[')
                for val in row:
                    lines.append(self.doprint(val) + ",")
                lines[-1] = lines[-1][:-1]
                lines.append(indent_str + '],')
            lines[-1] = lines[-1][:-1] + "], dtype=%s)" % str(expr.dtype)
            return "\n".join(lines)
        else:
            raise ValueError("Cannot render %s" % expr)

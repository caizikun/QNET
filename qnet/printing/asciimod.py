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
"""ASCII Printer"""
from ..algebra.singleton import Singleton
from .base import QnetBasePrinter
from .sympy import SympyStrPrinter
from .precedence import precedence, PRECEDENCE


class QnetAsciiPrinter(QnetBasePrinter):
    """Printer for a string (ASCII) representation.

    Attributes:
        _parenth_left (str): String to use for a left parenthesis
            (e.g. '\left(' in LaTeX). Used by :meth:`_split_op`
        _parenth_left (str): String to use for a right parenthesis
        _dagger_sym (str): Symbol that indicates the complex conjugate of an
            operator. Used by :meth:`_split_op`
        _tensor_sym (str): Symbol to use for tensor products. Used by
            :meth:`_render_hs_label`.
    """
    sympy_printer_cls = SympyStrPrinter
    printmethod = '_ascii'

    _parenth_left = '('
    _parenth_right = ')'
    _dagger_sym = 'H'
    _tensor_sym = '*'

    def _split_identifier(self, identifier):
        """Split the given identifier at the first underscore into (rendered)
        name and subscript. Both `name` and `subscript` are rendered as
        strings"""
        try:
            name, subscript = identifier.split("_", 1)
        except (TypeError, ValueError):
            name = identifier
            subscript = ''
        return self._str(name), self._str(subscript)

    def _split_op(
            self, identifier, hs_label=None, dagger=False, args=None):
        """Return `name`, total `subscript`, total `superscript` and
        `arguments` str. All of the returned strings are fully rendered.

        Args:
            identifier (str): An (non-rendered/ascii) identifier that may
                include a subscript. The output `name` will be the `identifier`
                without any subscript
            hs_label (str): The rendered label for the Hilbert space of the
                operator, or None. Returned unchanged.
            dagger (bool): Flag to indicate whether the operator is daggered.
                If True, :attr:`dagger_sym` will be included in the
                `superscript` (or  `subscript`, depending on the settings)
            args (list or None): List of arguments (expressions). Each element
                will be rendered with :meth:`doprint`. The total list of args
                will then be joined with commas, enclosed
                with :attr:`_parenth_left` and :attr:`parenth_right`, and
                returnd as the `arguments` string
        """
        name, total_subscript = self._split_identifier(identifier)
        total_superscript = ''
        if (hs_label not in [None, '']):
            if self._settings['show_hilbert_space'] == 'subscript':
                if len(total_subscript) == 0:
                    total_subscript = '(' + hs_label + ')'
                else:
                    total_subscript += ',(' + hs_label + ')'
            else:
                total_superscript += '(' + hs_label + ')'
        if dagger:
            total_superscript += self._dagger_sym
        args_str = ''
        if (args is not None) and (len(args) > 0):
            args_str = (self._parenth_left +
                        ",".join([self.doprint(arg) for arg in args]) +
                        self._parenth_right)
        return name, total_subscript, total_superscript, args_str

    def _render_hs_label(self, hs):
        """Return the label of the given Hilbert space as a string"""
        if isinstance(hs.__class__, Singleton):
            return self._str(hs.label)
        else:
            return self._tensor_sym.join(
                [self._str(ls.label) for ls in hs.local_factors])

    def _braket_fmt(self, expr_type):
        """Return a format string for printing an `expr_type`
        ket/bra/ketbra/braket"""
        mapping = {
            'bra': {
                True: '<{label}|^({space})',
                'subscript': '<{label}|_({space})',
                False:  '<{label}|'},
            'ket': {
                True: '|{label}>^({space})',
                'subscript': '|{label}>_({space})',
                False:  '|{label}>'},
            'ketbra': {
                True: '|{label_i}><{label_j}|^({space})',
                'subscript': '|{label_i}><{label_j}|_({space})',
                False:  '|{label_i}><{label_j}|'},
            'braket': {
                True: '<{label_i}|{label_j}>^({space})',
                'subscript': '<{label_i}|{label_j}>_({space})',
                False:  '<{label_i}|{label_j}>'},
        }
        hs_setting = bool(self._settings['show_hilbert_space'])
        if self._settings['show_hilbert_space'] == 'subscript':
            hs_setting = 'subscript'
        return mapping[expr_type][hs_setting]

    def _render_op(
            self, identifier, hs=None, dagger=False, args=None, superop=False):
        """Render an operator

        Args:
            identifier (str): The identifier (name/symbol) of the operator. May
                include a subscript, denoted by '_'.
            hs (qnet.algebra.hilbert_space_algebra.HilbertSpace): The Hilbert
                space in which the operator is defined
            dagger (bool): Whether the operator should be daggered
            args (list): A list of expressions that will be rendered with
                :meth:`doprint`, joined with commas, enclosed in parenthesis
            superop (bool): Whether the operator is a super-operator
        """
        hs_label = None
        if hs is not None and self._settings['show_hilbert_space']:
            hs_label = self._render_hs_label(hs)
        name, total_subscript, total_superscript, args_str \
            = self._split_op(identifier, hs_label, dagger, args)
        res = name
        if len(total_subscript) > 0:
            res += "_" + total_subscript
        if len(total_superscript) > 0:
            res += "^" + total_superscript
        if len(args_str) > 0:
            res += args_str
        return res

    def parenthesize(self, expr, level, *args, strict=False, **kwargs):
        """Render `expr` and wrap the result in parentheses if the precedence
        of `expr` is below the given `level` (or at the given `level` if
        `strict` is True. Extra `args` and `kwargs` are passed to the internal
        `doit` renderer"""
        needs_parenths = (
            (precedence(expr) < level) or
            ((not strict) and precedence(expr) <= level))
        if needs_parenths:
            return (
                self._parenth_left + self.doprint(expr, *args, **kwargs) +
                self._parenth_right)
        else:
            return self.doprint(expr, *args, **kwargs)

    def _print_CircuitSymbol(self, expr):
        return self._str(expr.name)

    def _print_CPermutation(self, expr):
        return r'Perm(%s)' % (
                ", ".join(map(self._str, expr.permutation)))

    def _print_SeriesProduct(self, expr):
        prec = precedence(expr)
        return " << ".join(
            [self.parenthesize(op, prec) for op in expr.operands])

    def _print_Concatenation(self, expr):
        prec = precedence(expr)
        reduced_operands = []  # reduce consecutive identities to a str
        id_count = 0
        for o in expr.operands:
            if self._isinstance(o, 'CIdentity'):
                id_count += 1
            else:
                if id_count > 0:
                    reduced_operands.append(
                        "cid({cdim}".format(cdim=id_count))
                    id_count = 0
                reduced_operands.append(o)
        return " + ".join(
            [self.parenthesize(op, prec) for op in reduced_operands])

    def _print_Feedback(self, expr):
        o, i = expr.out_in_pair
        return '[{operand}]_{{{output}->{input}}}'.format(
            operand=self.doprint(expr.operand), output=o, input=i)

    def _print_SeriesInverse(self, expr):
        return r'[{operand}]^{{-1}}'.format(
            operand=self.doprint(expr.operand))

    def _print_HilbertSpace(self, expr):
        return r'H_{label}'.format(
            label=self._render_hs_label(expr))

    def _print_ProductSpace(self, expr):
        return " * ".join(
            [self.doprint(op) for op in expr.operands])

    def _print_OperatorSymbol(self, expr, adjoint=False):
        return self._render_op(expr.identifier, expr._hs, dagger=adjoint)

    def _print_LocalOperator(self, expr, adjoint=False):
        if adjoint:
            dagger = not expr._dagger
        else:
            dagger = expr._dagger
        return self._render_op(
            expr._identifier, expr._hs, dagger=dagger, args=expr.args)

    def _print_LocalSigma(self, expr, adjoint=False):
        if self._settings['local_sigma_as_ketbra']:
            if adjoint:
                res = "|%s><%s|" % (expr.k, expr.j)
            else:
                res = "|%s><%s|" % (expr.j, expr.k)
            if self._settings['show_hilbert_space']:
                hs_label = self._render_hs_label(expr._hs)
                if self._settings['show_hilbert_space'] == 'subscript':
                    res += '_(%s)' % hs_label
                else:
                    res += '^(%s)' % hs_label
                return res
        else:
            if expr._is_projector:
                identifier = "%s_%s" % (expr._identifier, expr.j)
            else:
                if adjoint:
                    identifier = "%s_%s,%s" % (
                        expr._identifier, expr.k, expr.j)
                else:
                    identifier = "%s_%s,%s" % (
                        expr._identifier, expr.j, expr.k)
            return self._render_op(identifier, expr._hs, dagger=adjoint)

    def _print_IdentityOperator(self, expr):
        return "1"

    def _print_ZeroOperator(self, expr):
        return "0"

    def _print_OperatorPlus(self, expr, adjoint=False, superop=False):
        prec = precedence(expr)
        l = []
        kwargs = {}
        if adjoint:
            kwargs['adjoint'] = adjoint
        if superop:
            kwargs['superop'] = superop
        for term in expr.args:
            t = self.doprint(term, **kwargs)
            if t.startswith('-'):
                sign = "-"
                t = t[1:]
            else:
                sign = "+"
            if precedence(term) < prec:
                l.extend([sign, self._parenth_left + t + self._parenth_right])
            else:
                l.extend([sign, t])
        sign = l.pop(0)
        if sign == '+':
            sign = ""
        return sign + ' '.join(l)

    def _print_OperatorTimes(self, expr, **kwargs):
        prec = precedence(expr)
        return " * ".join(
            [self.parenthesize(op, prec, **kwargs) for op in expr.operands])

    def _print_ScalarTimesOperator(self, expr, product_sym=" * ", **kwargs):
        prec = PRECEDENCE['Mul']
        coeff, term = expr.coeff, expr.term
        term_str = self.doprint(term, **kwargs)
        if precedence(term) < prec:
            term_str = self._parenth_left + term_str + self._parenth_right

        if coeff == -1:
            if term_str.startswith(self._parenth_left):
                return "- " + term_str
            else:
                return "-" + term_str
        if 'adjoint' in kwargs:
            coeff_str = self.doprint(coeff, adjoint=kwargs['adjoint'])
        else:
            coeff_str = self.doprint(coeff)

        if term_str == '1':
            return coeff_str
        else:
            coeff_str = coeff_str.strip()
            if precedence(coeff) < prec and precedence(-coeff) < prec:
                # the above precedence check catches on only for true sums
                coeff_str = (
                    self._parenth_left + coeff_str + self._parenth_right)
            return coeff_str + product_sym + term_str.strip()

    def _print_Commutator(self, expr):
        return "[" + self.doprint(expr.A) + ", " + self.doprint(expr.B) + "]"

    def _print_OperatorTrace(self, expr):
        s = self._render_hs_label(expr._over_space)
        o = self.doprint(expr.operand)
        return r'tr_({space})[{operand}]'.format(space=s, operand=o)

    def _print_Adjoint(self, expr, adjoint=False):
        o = expr.operand
        if self._isinstance(o, 'LocalOperator'):
            if adjoint:
                dagger = o._dagger
            else:
                dagger = not o._dagger
            return self._render_op(
                o.identifier, hs=o.space, dagger=dagger, args=o.args[1:])
        elif self._isinstance(o, 'OperatorSymbol'):
            return self._render_op(
                o.identifier, hs=o.space, dagger=(not adjoint))
        else:
            if adjoint:
                return self.doprint(o)
            else:
                return (
                    self._parenth_left + self.doprint(o) +
                    self._parenth_right + "^" + self._dagger_sym)

    def _print_OperatorPlusMinusCC(self, expr):
        prec = precedence(expr)
        o = expr.operand
        sign_str = ' + '
        if expr._sign < 0:
            sign_str = ' - '
        return self.parenthesize(o, prec) + sign_str + "c.c."

    def _print_PseudoInverse(self, expr):
        prec = precedence(expr)
        return self.parenthesize(expr.operand, prec) + "^+"

    def _print_NullSpaceProjector(self, expr, adjoint=False):
        null_space_proj_sym = 'P_Ker'
        return self._render_op(
            null_space_proj_sym, hs=None, args=expr.operands, dagger=adjoint)

    def _print_KetSymbol(self, expr, adjoint=False):
        if adjoint:
            fmt = self._braket_fmt('bra')
        else:
            fmt = self._braket_fmt('ket')
        return fmt.format(
            label=self._str(expr.label),
            space=self._render_hs_label(expr.space))

    def _print_ZeroKet(self, expr, adjoint=False):
        return "0"

    def _print_TrivialKet(self, expr, adjoint=False):
        return "1"

    def _print_CoherentStateKet(self, expr, adjoint=False):
        if adjoint:
            fmt = self._braket_fmt('bra')
        else:
            fmt = self._braket_fmt('ket')
        return fmt.format(
            label=(self._str('alpha=') + self.doprint(expr._ampl)),
            space=self._render_hs_label(expr.space))

    def _print_KetPlus(self, expr, adjoint=False):
        # this behaves exactly like Operators
        return self._print_OperatorPlus(expr, adjoint=adjoint)

    def _print_TensorKet(self, expr, adjoint=False):
        if expr._label is None:
            prec = precedence(expr)
            kwargs = {}
            if adjoint:
                kwargs['adjoint'] = adjoint
            tensor_sym = " %s " % self._tensor_sym
            return tensor_sym.join([
                self.parenthesize(op, prec, **kwargs)
                for op in expr.operands])
        else:  # "trivial" product of LocalKets
            fmt = self._braket_fmt('ket')
            if adjoint:
                fmt = self._braket_fmt('bra')
            label = ",".join([self._str(o.label) for o in expr.operands])
            space = self._render_hs_label(expr.space)
            return fmt.format(label=label, space=space)

    def _print_ScalarTimesKet(self, expr, adjoint=False):
        prec = precedence(expr)
        coeff, term = expr.coeff, expr.term
        kwargs = {}
        if adjoint:
            kwargs['adjoint'] = adjoint
        term_str = self.parenthesize(term, prec, **kwargs)

        if coeff == -1:
            if term_str.startswith(self._parenth_left):
                return "- " + term_str
            else:
                return "-" + term_str
        coeff_str = self.doprint(coeff, **kwargs)
        return (coeff_str.strip() + ' * ' + term_str.strip())

    def _print_OperatorTimesKet(self, expr, adjoint=False):
        prec = precedence(expr)
        op, ket = expr.operator, expr.ket
        kwargs = {}
        if adjoint:
            kwargs['adjoint'] = adjoint
        rendered_op = self.parenthesize(op, prec, **kwargs)
        rendered_ket = self.parenthesize(ket, prec, **kwargs)
        if adjoint:
            return rendered_ket + " " + rendered_op
        else:
            return rendered_op + " " + rendered_ket

    def _print_Bra(self, expr, adjoint=False):
        return self.doprint(expr.ket, adjoint=(not adjoint))

    def _print_BraKet(self, expr, adjoint=False):
        trivial = True
        try:
            bra_label = str(expr.bra.label)
        except AttributeError:
            trivial = False
        try:
            ket_label = str(expr.ket.label)
        except AttributeError:
            trivial = False
        if trivial:
            fmt = self._braket_fmt('braket')
            if adjoint:
                return fmt.format(
                    label_i=self._str(ket_label),
                    label_j=self._str(bra_label),
                    space=self._render_hs_label(expr.ket.space))
            else:
                return fmt.format(
                    label_i=self._str(bra_label),
                    label_j=self._str(ket_label),
                    space=self._render_hs_label(expr.ket.space))
        else:
            prec = precedence(expr)
            rendered_bra = self.parenthesize(expr.bra, prec, adjoint=adjoint)
            rendered_ket = self.parenthesize(expr.ket, prec, adjoint=adjoint)
            if adjoint:
                return rendered_ket + ' * ' + rendered_bra
            else:
                return rendered_bra + ' * ' + rendered_ket

    def _print_KetBra(self, expr, adjoint=False):
        trivial = True
        try:
            bra_label = str(expr.bra.label)
        except AttributeError:
            trivial = False
        try:
            ket_label = str(expr.ket.label)
        except AttributeError:
            trivial = False
        if trivial:
            fmt = self._braket_fmt('ketbra')
            if adjoint:
                return fmt.format(
                    label_i=self._str(bra_label),
                    label_j=self._str(ket_label),
                    space=self._render_hs_label(expr.ket.space))
            else:
                return fmt.format(
                    label_i=self._str(ket_label),
                    label_j=self._str(bra_label),
                    space=self._render_hs_label(expr.ket.space))
        else:
            prec = precedence(expr)
            rendered_bra = self.parenthesize(expr.bra, prec, adjoint=adjoint)
            rendered_ket = self.parenthesize(expr.ket, prec, adjoint=adjoint)
            if adjoint:
                return rendered_bra + rendered_ket
            else:
                return rendered_ket + rendered_bra

    def _print_SuperOperatorSymbol(self, expr, adjoint=False, superop=True):
        return self._render_op(
            expr.label, expr._hs, dagger=adjoint, superop=True)

    def _print_IdentitySuperOperator(self, expr):
        return "1"

    def _print_ZeroSuperOperator(self, expr):
        return "0"

    def _print_SuperOperatorPlus(self, expr, adjoint=False, superop=True):
        return self._print_OperatorPlus(expr, adjoint=adjoint, superop=True)

    def _print_SuperOperatorTimes(self, expr, adjoint=False, superop=True):
        return self._print_OperatorTimes(expr, adjoint=adjoint, superop=True)

    def _print_ScalarTimesSuperOperator(
            self, expr, adjoint=False, superop=True):
        return self._print_ScalarTimesOperator(
            expr, adjoint=adjoint, superop=True)

    def _print_SuperAdjoint(self, expr, adjoint=False, superop=True):
        o = expr.operand
        if self._isinstance(o, 'SuperOperatorSymbol'):
            return self._render_op(
                o.label, hs=o.space, dagger=(not adjoint), superop=True)
        else:
            if adjoint:
                return self.doprint(o)
            else:
                return (
                    self._parenth_left + self.doprint(o) +
                    self._parenth_right + "^" + self._dagger_sym)

    def _print_SPre(self, expr, superop=True):
        return (
            "SPre" + self._parenth_left + self.doprint(expr.operands[0]) +
            self._parenth_right)

    def _print_SPost(self, expr, superop=True):
        return (
            "SPost" + self._parenth_left + self.doprint(expr.operands[0]) +
            self._parenth_right)

    def _print_SuperOperatorTimesOperator(self, expr):
        prec = precedence(expr)
        sop, op = expr.sop, expr.op
        cs = self.parenthesize(sop, prec)
        ct = self.doprint(op)
        return "%s[%s]" % (cs, ct)


def ascii(expr, cache=None, **settings):
    """Return an ascii textual representation of the given object /
    expression"""
    try:
        if cache is None and len(settings) == 0:
            return ascii.printer.doprint(expr)
        else:
            printer = ascii._printer_cls(cache, settings)
            return printer.doprint(expr)
    except AttributeError:
        # init_printing was not called. Setting up defaults
        ascii._printer_cls = QnetAsciiPrinter
        ascii.printer = ascii._printer_cls()
        return ascii(expr, cache, **settings)

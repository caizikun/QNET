#This file is part of QNET.
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

"""
Component definition file for a simple linear cavity model with two ports.
See documentation of :py:class:`LinearCavity`.
"""
from sympy.core.symbol import symbols
from sympy import sqrt

from qnet.circuit_components.component import Component, SubComponent
from qnet.algebra.circuit_algebra import SLH
from qnet.algebra.matrix_algebra import Matrix, identity_matrix
from qnet.algebra.operator_algebra import Destroy
from qnet.algebra.hilbert_space_algebra import LocalSpace


__all__ = ["LinearCavity"]


class LinearCavity(Component):
    r"""
    This model describes a cavity model with two ports.

    The model's SLH parameters are given by

    .. math::
        S & = \mathbf{1}_2 \\
        L & = \begin{pmatrix} \sqrt{\kappa_1} a \\ \sqrt{\kappa_2} a \end{pmatrix} \\
        H &= \Delta a^\dagger a

    This particular component definition explicitly captures the reducibility of a trivial scattering matrix.
    I.e., it can be reduced into separate :py:class:`CavityPort` models for each port.
    """

    CDIM = 2

    PORTSIN = ['In1', 'In2']
    PORTSOUT = ['Out1', 'Out2']

    sub_blockstructure = (1, 1)

    Delta = symbols('Delta', real = True)       # Detuning from cavity
    kappa_1 = symbols('kappa_1', real = True)   # coupling through first port
    kappa_2 = symbols('kappa_2', real = True)   # coupling through second port
    FOCK_DIM = 75
    _parameters = ['Delta', 'kappa_1', 'kappa_2', 'FOCK_DIM']

    @property
    def space(self):
        return LocalSpace(self.name, dimension=self.FOCK_DIM)

    @property
    def port1(self):
        return CavityPort(self, 0)

    @property
    def port2(self):
        return CavityPort(self, 1)

    def _creduce(self):
        return self.port1 + self.port2

    def _toSLH(self):
        return self.creduce().toSLH()

    def _toABCD(self, linearize):
        return self.toSLH().toABCD(linearize)


class CavityPort(SubComponent):
    """
    Sub component model for the individual ports of a :py:class:`LinearCavity`.
    The Hamiltonian is included with the first port.
    """

    def _toSLH(self):

        a = Destroy(hs=self.space)
        a_d = a.adjoint()
        S = identity_matrix(1)

        if self.sub_index == 0:
            # Include the Hamiltonian only with the first port of the kerr
            # cavity circuit object
            H = self.Delta * (a_d * a)
            L = Matrix([[sqrt(self.kappa_1) * a]])
        else:
            H = 0
            L = Matrix([[sqrt(self.kappa_2) * a]])

        return SLH(S, L, H)

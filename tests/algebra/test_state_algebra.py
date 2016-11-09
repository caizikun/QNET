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
# Copyright (C) 2012-2013, Nikolas Tezak
#
###########################################################################


import unittest

from sympy import sqrt, exp, I, pi

from qnet.algebra.operator_algebra import (
        OperatorSymbol, Create, Destroy, Jplus, Jminus, Jz, Phase, Displace,
        LocalSigma, IdentityOperator)
from qnet.algebra.hilbert_space_algebra import LocalSpace
from qnet.algebra.state_algebra import (
        KetSymbol, ZeroKet, KetPlus, ScalarTimesKet, CoherentStateKet,
        TrivialKet, UnequalSpaces, TensorKet, BasisKet)
import pytest


class TestStateAddition(unittest.TestCase):

    def testAdditionToZero(self):
        hs = LocalSpace("hs")
        a = KetSymbol("a", hs)
        z = ZeroKet
        assert a+z == a
        assert z+a == a
        assert z+z == z
        assert z == 0


    def testAdditionToOperator(self):
        hs = LocalSpace("hs")
        a = KetSymbol("a", hs)
        b = KetSymbol("b", hs)
        assert a + b == b + a
        assert a + b == KetPlus(a,b)

    def testSubtraction(self):
        hs = LocalSpace("hs")
        a = KetSymbol("a", hs)
        b = KetSymbol("b", hs)
        z = ZeroKet
        lhs = a - a
        assert lhs == z
        lhs = a - b
        rhs = KetPlus(a, ScalarTimesKet(-1,b))
        assert lhs == rhs

    def testHilbertSpace(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        with pytest.raises(UnequalSpaces):
            a.__add__(b)


    def testEquality(self):
        h1 = LocalSpace("h1")
        assert CoherentStateKet(h1, 10.)+CoherentStateKet(h1, 20.) == CoherentStateKet(h1, 20.)+CoherentStateKet(h1, 10.)





class TestTensorKet(unittest.TestCase):

    def testIdentity(self):
        h1 = LocalSpace("h1")
        a = KetSymbol("a", h1)
        id = TrivialKet
        assert a * id == a
        assert id * a == a

    def testOrdering(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        assert a * b == TensorKet(a,b)
        assert a * b == b * a


    def testHilbertSpace(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        assert a.space == h1
        assert (a * b).space == h1*h2


    def testEquality(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")

        assert CoherentStateKet(h1, 1)*CoherentStateKet(h2, 2) == CoherentStateKet(h2, 2) * CoherentStateKet(h1, 1)


class TestScalarTimesKet(unittest.TestCase):
    def testZeroOne(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        z = ZeroKet

        assert a+a == 2*a
        assert a*1 == a
        assert 1*a == a
        assert a*5 == ScalarTimesKet(5, a)
        assert 5*a == a*5
        assert 2*a*3 == 6*a
        assert a*5*b == ScalarTimesKet(5, a*b)
        assert a*(5*b) == ScalarTimesKet(5, a*b)

        assert 0 * a == z
        assert a * 0 == z
        assert 10 * z == z


    def testScalarCombination(self):
        a = KetSymbol("a", "h1")
        assert a+a == 2*a
        assert 3 * a + 4 * a == 7 * a
        assert CoherentStateKet(1, "1") + CoherentStateKet(1, "1") == 2 * CoherentStateKet(1, "1")

    def testHilbertSpace(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        assert (5*(a * b)).space == h1*h2


class TestOperatorTimesKet(unittest.TestCase):

    def testZeroOne(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        A = OperatorSymbol("A", h1)
        Ap = OperatorSymbol("Ap", h1)
        B = OperatorSymbol("B", h2)

        assert IdentityOperator*a == a
        assert A * (Ap * a) == (A * Ap) * a
        assert (A * B) * (a * b) == (A * a) * (B * b)



    def testScalarCombination(self):
        a = KetSymbol("a", "h1")
        assert a+a == 2*a
        assert 3 * a + 4 * a == 7 * a
        assert CoherentStateKet(1, "1") + CoherentStateKet(1, "1") == 2 * CoherentStateKet(1, "1")

    def testHilbertSpace(self):
        h1 = LocalSpace("h1")
        h2 = LocalSpace("h2")
        a = KetSymbol("a", h1)
        b = KetSymbol("b", h2)
        assert (5*(a * b)).space == h1*h2



class TestLocalOperatorKetRelations(unittest.TestCase):

    def testCreateDestroy(self):
        assert Create(1) * BasisKet(1, 2) == sqrt(3) * BasisKet(1, 3)
        assert Destroy(1) * BasisKet(1, 2) == sqrt(2) * BasisKet(1, 1)
        assert Destroy(1) * BasisKet(1, 0) == ZeroKet
        lhs = Destroy(1) * CoherentStateKet(1, 10.)
        rhs = 10 * CoherentStateKet(1, 10.)
        assert lhs == rhs

    def testSpin(self):
        j = 3
        h = LocalSpace("j", basis=range(-j,j+1))

        assert Jplus(h) * BasisKet(h, 2) == sqrt(j*(j+1)-2*(2+1)) * BasisKet(h, 3)
        assert Jminus(h) * BasisKet(h, 2) == sqrt(j*(j+1)-2*(2-1)) * BasisKet(h, 1)
        assert Jz(h) * BasisKet(h, 2) == 2 * BasisKet(h, 2)


    def testPhase(self):
        assert Phase(1, 5) * BasisKet(1, 3) == exp(I * 15) * BasisKet(1, 3)
        lhs = Phase(1, pi) * CoherentStateKet(1, 3.)
        rhs = CoherentStateKet(1, -3.)
        assert lhs.__class__ == rhs.__class__
        assert lhs.space == rhs.space
        assert abs(lhs.ampl - rhs.ampl) < 1e-14

    def testDisplace(self):
        assert Displace(1, 5 + 6j) * CoherentStateKet(1, 3.) == exp(I * ((5+6j)*3).imag) * CoherentStateKet(1, 8 + 6j)
        assert Displace(1, 5 + 6j) * BasisKet(1,0) == CoherentStateKet(1, 5+6j)

    def testLocalSigmaPi(self):
        assert LocalSigma(1, 0, 1) * BasisKet(1, 1) == BasisKet(1, 0)
        assert LocalSigma(1, 0, 0) * BasisKet(1, 1) == ZeroKet

    def testActLocally(self):
        assert (Create(1) * Destroy(2)) * (BasisKet(1, 2) * BasisKet(2, 1)) == sqrt(3) * BasisKet(1, 3) * BasisKet(2,0)


    def testOperatorTensorProduct(self):
        assert (Create(1)*Destroy(2))*(BasisKet(1,0)*BasisKet(2,1)) == BasisKet(1,1)*BasisKet(2,0)

    def testOperatorProduct(self):
        assert (Create(1)*Destroy(1))*(BasisKet(1,1)*BasisKet(2,1)) == BasisKet(1,1)*BasisKet(2,1)
        assert (Create(1)*Destroy(1)*Destroy(1))*(BasisKet(1,2)*BasisKet(2,1)) == sqrt(2)*BasisKet(1,1)*BasisKet(2,1)
        assert (Create(1)*Destroy(1)*Destroy(1))*BasisKet(1,2) == sqrt(2)*BasisKet(1,1)
        assert (Create(1)*Destroy(1))*BasisKet(1,1) == BasisKet(1,1)
        assert (Create(1) * Destroy(1)) * BasisKet(1,0) == ZeroKet


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

from qnet.algebra.operator_algebra import *
from qnet.algebra.circuit_algebra import _time_dependent_to_qutip
from sympy import symbols
import numpy as np
import qutip
import unittest

class TestQutipConversion(unittest.TestCase):

    def testCreateDestoy(self):
        H = local_space("H", dimension = 5)
        ad = Create(H)
        a = Create(H).adjoint()
        aq = a.to_qutip()
        for k in range(H.dimension - 1):
            self.assertLess(abs(aq[k, k+1] - sqrt(k + 1)), 1e-10)
        self.assertEqual(ad.to_qutip(),qutip.dag(a.to_qutip()))

    def testN(self):
        H = local_space("H", dimension = 5)
        ad = Create(H)
        a = Create(H).adjoint()
        aq = a.to_qutip()
        n = ad * a
        nq = n.to_qutip()
        for k in range(H.dimension):
            self.assertLess(abs(nq[k,k] - k), 1e-10)

    def testSigma(self):
        H = local_space("H", basis = ("e","g","h"))
        sigma = LocalSigma(H, 'g', 'e')
        sq = sigma.to_qutip()
        self.assertEqual(sq[1,0], 1)
        self.assertEqual((sq**2).norm(), 0)

    def testPi(self):
        H = local_space("H", basis = ("e","g","h"))
        Pi_h = LocalProjector(H, 'h')
        self.assertEqual(Pi_h.to_qutip().tr(), 1)
        self.assertEqual(Pi_h.to_qutip()**2, Pi_h.to_qutip())

    def testTensorProduct(self):
        H = local_space("H1", dimension = 5)
        ad = Create(H)
        a = Create(H).adjoint()
        H2 = local_space("H2", basis = ("e","g","h"))
        sigma = LocalSigma(H2, 'g', 'e')
        self.assertEqual((sigma * a).to_qutip(), qutip.tensor(a.to_qutip(), sigma.to_qutip()))

    def testLocalSum(self):
        H = local_space("H1", dimension = 5)
        ad = Create(H)
        a = Create(H).adjoint()
        self.assertEqual((a + ad).to_qutip(), a.to_qutip() + ad.to_qutip())

    def testNonlocalSum(self):
        H = local_space("H1", dimension = 5)
        ad = Create(H)
        a = Create(H).adjoint()
        H2 = local_space("H2", basis = ("e","g","h"))
        sigma = LocalSigma(H2, 'g', 'e')
        self.assertEqual((a + sigma).to_qutip()**2, ((a + sigma)*(a + sigma)).to_qutip())

    def testScalarCoeffs(self):
        H = local_space("H1", dimension = 5)
        ad = Create(H)
        a = Create(H).adjoint()
        self.assertEqual(2 * a.to_qutip(), (2 * a).to_qutip())


    def testSymbol(self):
        expN = OperatorSymbol("expN", 1)
        N = Create(1)*Destroy(1)
        N.space.dimension = 10

        M = Create(2)*Destroy(2)
        M.space.dimension = 5

        converter1 = {
            expN: lambda fs: N.to_qutip().expm()
        }
        with represent_symbols_as(converter1):
            expNq = expN.to_qutip()

        assert np.linalg.norm(expNq.data.toarray()
            - (N.to_qutip().expm().data.toarray())) < 1e-8

        with represent_symbols_as(converter1):
            expNMq = (expN*M).to_qutip()

        assert np.linalg.norm(expNMq.data.toarray()
            - (qutip.tensor(N.to_qutip().expm(),
                            M.to_qutip()).data.toarray())) < 1e-8

        def converter2(obj, full_space=None):
            if obj == expN:
                return N.to_qutip(full_space=full_space).expm()
            else:
                raise ValueError(str(obj))

        with represent_symbols_as(converter2):
            expNq = expN.to_qutip()

        assert np.linalg.norm(expNq.data.toarray()
            - (N.to_qutip().expm().data.toarray())) < 1e-8


        with represent_symbols_as(converter2):
            expNMq = (expN*M).to_qutip()

        assert np.linalg.norm(expNMq.data.toarray()
            - (qutip.tensor(N.to_qutip().expm(),
                            M.to_qutip()).data.toarray())) < 1e-8







def test_time_dependent_to_qutip():
    Hil = local_space("H", dimension=5)
    ad = Create(Hil)
    a = Create(Hil).adjoint()

    w, g, t = symbols('w, g, t', real=True)

    H =  ad*a + (a + ad)
    assert _time_dependent_to_qutip(H) == H.to_qutip()

    H =  g * t * a
    res = _time_dependent_to_qutip(H, time_symbol=t)
    assert res[0] == a.to_qutip()
    assert res[1](1, {}) == g
    assert res[1](1, {g: 2}) == 2

    H =  ad*a + g* t * (a + ad)
    res = _time_dependent_to_qutip(H, time_symbol=t)
    assert len(res) == 3
    assert res[0] == (ad*a).to_qutip()
    assert res[1][0] == ad.to_qutip()
    assert res[1][1](1, {}) == g
    assert res[2][0] == a.to_qutip()
    assert res[2][1](1, {}) == g

    res = _time_dependent_to_qutip(H, time_symbol=t, convert_as='str')
    terms = [term for H, term in res[1:]]
    assert terms == ['g*t', 'g*t']

    H =  (ad*a + t * (a + ad))**2
    res = _time_dependent_to_qutip(H, time_symbol=t, convert_as='str')
    assert len(res) == 9
    terms = [term for H, term in res[1:]]
    assert terms == ['t**2', 't', 't', 't**2', '2*t', '2*t**2 + 1', '2*t',
                     't**2']
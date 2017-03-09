import os
import sys
from distutils.core import setup
from pkgutil import walk_packages
# from distutils.extension import Extension
#
# from Cython.Distutils import build_ext
# import numpy as np
#
#
# ext_modules = [
#     Extension("qnet.misc.kerr_cysolve",
#               ["qnet/misc/src/kerr_cysolve.pyx"],
#               include_dirs=[np.get_include()],
#               extra_link_args=['-lm']),
# ]


def get_version(filename):
    """Extract the package version"""
    with open(filename) as in_fh:
        for line in in_fh:
            if line.startswith('__version__'):
                return line.split('=')[1].strip()[1:-1]
    raise ValueError("Cannot extract version from %s" % filename)


version = get_version('qnet/__init__.py')


def find_packages(path=".", prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name

os.path.realpath(__file__)
packages = list(find_packages('qnet', 'qnet'))

setup(
    name='QNET',
    version=version,
    description="Tools for symbolically analyzing quantum feedback networks.",
    scripts=["bin/parse_qhdl.py"],
    author="Nikolas Tezak, Michael Goerz",
    author_email="mail@michaelgoerz.net",
    url="http://github.com/mabuchilab/QNET",
    # cmdclass={'build_ext': build_ext},
    packages=packages,
    # ext_modules=ext_modules,
    install_requires=[
        'matplotlib',
        'sympy',
        'ply',
        'six',
        'numpy',
    ],
    extras_require={
        'dev': ['click', 'pytest', 'sphinx', 'sphinx-autobuild',
                'sphinx_rtd_theme', 'better-apidoc', 'nose', 'cython',
                'coverage', 'pytest-cov', 'pytest-capturelog',
                'pytest-xdist'],
        'simulation': ['cython', 'qutip>=3.0.1'],
        'circuit_visualization': 'pyx>0.13',
    },
    dependency_links=[
        "http://downloads.sourceforge.net/project/pyx/pyx/0.13/"
        + "PyX-0.13.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects"
        + "%2Fpyx%2Ffiles%2F&ts=1423687678&use_mirror=iweb",
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)


QNET
====

The QNET package is a set of tools created and compiled to aid in the design and analysis of photonic circuit models.
The physical systems that can be modeled within the framework include quantum optical experiments that can be described as nodes with internal degrees of freedom such as interacting quantum harmonic oscillators and/or N-level quantum systems that,
in turn are coupled to a finite number of external bosonic quantum fields.

Contents
--------

The package consists of the following components:

1. A symbolic computer algebra package `qnet.algebra` for Hilbert Space quantum mechanical operators, the Gough-James circuit algebra and also an algebra for Hilbert space states and Super-operators.
2. The [QHDL][] language definition and parser `qnet.qhdl` including a front-end located at `bin/parse_qhdl.py` that can convert a QHDL-file into a circuit component library file.
3. A library of existing primitive or composite circuit components `qnet.circuit_components` that can be embedded into a new circuit definition.

Dependencies
------------

In addition to these core components, the software uses the following existing software packages:

0. [Python][] version 2.6 or higher. QNET is still officially a Python 2 package, but migration to Python 3 should not be too hard to achieve.
1. The [gEDA][] toolsuite for its visual tool `gschem` for the creation of circuits end exporting these to QHDL `gnetlist`. We have created device symbols for our primitive circuit components to be used with `gschem` and we have included our own `gnetlist` plugin for exporting to QHDL.
2. The [SymPy][] symbolic algebra Python package to implement symbolic 'scalar' algebra, i.e. the coefficients of state, operator or super-operator expressions can be symbolic SymPy expressions as well as pure python numbers.
3. The [QuTiP][] python package as an extremely useful, efficient and full featured numerical backend. Operator expressions where all symbolic scalar parameters have been replaced by numeric ones, can be converted to (sparse) numeric matrix representations, which are then used to solve for the system dynamics using the tools provided by QuTiP.
4. The [PyX][] python package for visualizing circuit expressions as box/flow diagrams.
5. The [SciPy][] and [NumPy][] packages (needed for QuTiP but also by the `qnet.algebra` package)
6. The [PLY][] python package as a dependency of our Python Lex/Yacc based QHDL parser.

A convenient way of obtaining Python as well as some of the packages listed here (SymPy, SciPy, NumPy, PLY) is to download the [Enthought][] Python Distribution (EPD) which is free for academic use.
A highly recommended way of working with QNET and QuTiP and just scientific python codes in action is to use the excellent [IPython][] shell which comes both with a command-line interface as well as a very polished browser-based notebook interface.

Installation/Configuration
--------------------------

Copy the QNET folder to any location you'd like. We will tell python how to find it by setting the `$PYTHONPATH` environment variable to include the QNET directory's path.
Append the following to your local bash configuration `$HOME/.bashrc` or something equivalent.

    export QNET=/path/to/cloned/repository
    export PYTHONPATH=$QNET:$PYTHONPATH

On Windows a similar procedure should exist. Environment variable can generally be set via the windows control panels.
It should be sufficient to set just the `PYTHONPATH` environment variable.


To configure gEDA to include our special quantum circuit component symbols you will need to copy the following configuration files from the `$QNET/gEDA_support/config` directory to the `$HOME/.gEDA` directory:
- `~/.gEDA/gafrc`
- `~/.gEDA/gschemrc`

Then install the QHDL netlister plugin within gEDA by creating a symbolic link

    ln -s $QNET/gEDA_support/gnet-qhdl.scm  /path/to/gEDA_resources_folder/scheme/gnet-qhdl.scm

in my case that path is given by `/opt/local/share/gEDA`, but in general simply look for the gEDA-directory that contains the file named `system-gafrc`.

Using QNET in practice
----------------------

A possible full workflow using QNET is thus:

I. Use `gschem` (of gEDA) to graphically design a circuit model.
II. Export the schematic to QHDL using `gnetlist` (also part of gEDA)
III. Parse the QHDL-circuit definition file into a Python circuit library component using the parser front-end `bin/parse_qhdl.py`.
IV. Analyze the model analytically using our symbolic algebra and/or numerically using QuTiP.

This package is still work in progress and as it is developed by a single developer, documentation and comprehensive testing code is still somewhat lacking.
Any contributions, bug reports and general feedback from end-users would be highly appreciated. If you have found a bug, it would be extremely helpful if you could try to write a minimal code example that reproduces the bug.
Feature requests will definitely be considered. Higher priority will be given to things that many people ask for and that can be implemented efficiently.

To learn of how to carry out each of these steps, we recommend looking at the provided examples and reading the relevant sections in the QNET manual.
Also, if you want to implement and add your own primitive device models, please consult the QNET manual.

Acknowledgements
----------------

All QNET code was written by Nikolas Tezak, but at the request of Hideo Mabuchi who had the original idea for this package.
N. Tezak would like to acknowledge the following people's support which included their vision, ideas, examples, bug reports and feedback.

- Hideo Mabuchi
- Michael Armen
- Armand Niederberger
- Joe Kerckhoff
- Dmitri Pavlichin
- Gopal Sarma
- Ryan Hamerly
- Michael Hush

Work on QNET was directly supported by DARPA-MTO under Award No. N66001-11-1-4106, by the National Science Foundation under Grant No. PHY-1005386.
Nikolas Tezak is also supported by a Simons Foundation Math+X fellowship as well as a Stanford Graduate Fellowship.


[Python] http://www.python.org
[gEDA] http://www.gpleda.org
[QHDL] http://rsta.royalsocietypublishing.org/content/370/1979/5270.abstract
[QNET] http://mabuchilab.github.com/QNET/
[SymPy] http://SymPy.org/
[QuTiP] https://code.google.com/p/qutip/
[PyX] http://pyx.sourceforge.net/
[SciPy] http://www.scipy.org/
[NumPy] http://numpy.scipy.org/
[PLY] http://www.dabeaz.com/ply/
[Enthought] http://www.enthought.com/
[IPython] http://ipython.org/
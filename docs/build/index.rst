==============================================
Building wheels and docs and running the tests
==============================================

First clone the repository

.. code-block:: console
    :class: admonition

    $ git clone git@github.com:chdemko/py-part.git
    $ cd py-part


Building the docs
=================

.. code-block:: console
    :class: admonition

    $ pip install .[docs]
    $ python setup.py build_sphinx

Building the wheel with cython
==============================

.. code-block:: console
    :class: admonition

    $ pip install .[build]
    $ python setup.py bdist --cythonize

Building the wheel
==================

.. code-block:: console
    :class: admonition

    $ pip install .
    $ python setup.py bdist

Running the tests
=================

.. code-block:: console
    :class: admonition

    $ pip install tox
    $ tox -e py



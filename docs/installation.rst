.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Ariadne Extended, run this command in your terminal:

.. code-block:: console

    $ pip install ariadne-extended

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

Or with `Poetry <https://python-poetry.org/>`_ :

.. code-block:: console

    $ poetry add ariadne-extended

These two ways are the preferred method to install Ariadne Extended, as it will always install the most recent stable release.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Setup
=====

Ariadne extended is split up into different django apps depending on what graphql functionality you're wanting.

One requirement of the provided apps is to enable the graph loader app `ariadne_extended.graph_loader`.

.. code-block:: python

    INSTALLED_APPS = (
        "ariadne_extended.graph_loader",
        "ariadne_extended.cursor_pagination",
        "ariadne_extended.payload",
        "ariadne_extended.uuid",
        "ariadne_extended.contrib.waffle_graph"
    )

From sources
------------

The sources for Ariadne Extended can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/patriotresearch/ariadne-extended

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/patriotresearch/ariadne-extended/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/patriotresearch/ariadne-extended
.. _tarball: https://github.com/patriotresearch/ariadne-extended/tarball/master

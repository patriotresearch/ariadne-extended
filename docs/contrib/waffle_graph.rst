============
Waffle Graph
============

The waffle graph contrib app supplies resolvers and schema to be used with the `django-waffle <https://waffle.readthedocs.io/en/stable/>`_ feature switching module.

This will enable you to query for waffle flags, switches and samples that are enabled/disabled in your graphql queries and make them available to your UI.

Setup
=====

Make sure you have installed `django-waffle <https://waffle.readthedocs.io/en/stable/>`_ and setup in your app already.

To include the waffle schema and resolvers in your app simply add the `waffle_graph` to your `INSTALLED_APPS`.

.. code-block:: python

    INSTALLED_APPS = (
        "waffle",
        "ariadne_extended.graph_loader",
        ...
        "ariadne_extended.contrib.waffle_graph"
    )

Run your migrations and check the django admin, add a flag and run some queries.

Schema
======

Once added to your installed apps, these types and extensions will become available for use within your own graphql schema and queries.

.. literalinclude:: ../../ariadne_extended/contrib/waffle_graph/schema.graphql

Resolvers
=========

.. automodule:: ariadne_extended.contrib.waffle_graph.resolvers
    :members:

.. .. autoclass:: ariadne_extended.contrib.waffle_graph.resolvers.WaffleResolver
..     :members:

Examples
========

Example of a query that retrieves all data.

.. code:: 

    query {
        waffle {
            flags {
                ...BaseWaffleItem
            }
            flagDefault
            switches {
                ...BaseWaffleItem
            }
            switchDefault
            samples {
                ...BaseWaffleItem
            }
            sampleDefault
        }
    }
    fragment BaseWaffleItem on WaffleItem {
        name
        active
        note
    }}

Example of retrieving a flag that exists and one that doesn't.

The flag that doesn't exist will return the waffle default value for active for that type.

.. code::

    query {
        waffle {
            goodFlag: flag(name: "flag0") {
                ...BaseWaffleItem
            }
            badFlag: flag(name: "Doesn't exist") {
                ...BaseWaffleItem
            }
        }
    }
    fragment BaseWaffleItem on WaffleItem {
        name
        active
        note
    }

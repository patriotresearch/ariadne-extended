Permissions
===========

There is a permission system built into ariadne-extended and is
backwards compatible with django-rest-framework because we have
effectively forked their base permission classes. From there they are
tweaked to be used specifically for resolvers.

Global Permissions
------------------

You can set a global set of permissions in your settings file using the
``ARIADNE_SETTINGS`` dictionary. By setting
``DEFAULT_PERMISSION_CLASSES`` in your ``settings.py``.

.. code:: python

    ARIADNE_EXTENDED = {
        'DEFAULT_PERMISSION_CLASSES': [
            'ariadne_extended.permissions.AllowAny',
        ]
    }

Resolver Level Permissions
--------------------------

Since the default global permission is to ``AllowAny`` we might want to
only allow autheticated users to use a resolver.

.. code:: python

    from ariadne_extended.resolvers import Resolver
    from ariadne_extended import permissions

    class MoneyMakeingResolver(Resolver):
        permission_classes = [permissions.IsAuthenticated]

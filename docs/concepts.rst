========
Concepts
========

Ariadne uses function based resolvers to resolve fields from a graphql schema. This mirrors the way django deals with views. There is also the additional concept of class based views which is unimplemented in ariadne as the library does not primarily focus on a Django integration.


Class Based Resolvers (CBR)
===========================

This module introduces the concept of class based resolvers that act in similar ways to Django's class based views and Django REST Framework views.

These CBRs return the final python type or structure that a graphql schema field is expecting in order to resolve correctly. By designing these resolvers as classes we're able to re-use existing mixins that enable or disable resolver behavior. We utilize this to generalize the interface with Django models and provide re-usable patterns for activities like pagination and mutation input validation.

If you're unfamiliar with Class Based Views or Django REST Framework classes you can familiarize yourself with their patterns are the helpful Classy documentation sites. `Classy Django REST Framework <http://www.cdrf.co/>`_ and `Classy Class-Based Views <https://ccbv.co.uk/>`_ .

CBR and async Django
--------------------

.. note:: Async CBR resolvers are not yet supported

Django has plans to introduce asynchronous views and ORM features in future versions. Once that transition has begun the Ariadne Extended module will make efforts to also support async field resolvers. Currently it does not support ariadne async features.

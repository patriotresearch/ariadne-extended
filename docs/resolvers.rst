=========
Resolvers
=========

Abstract CBR
============

All CBRs should inherit from the **Resolver** class

This class found in the resolvers module: `ariadne_extended.resolvers.Resolver`

To use a CBR as a field resolver there are a few

Resolver flow:
==============
When a field attempts to resolve using a CBR the class initializes a new instance with parameters from the the field and information about any parent field and graphql info context ( the ariadne info parameter ).

The `initial` method is called with the info context and subsequently checks for field access permission and any field throttling.

Afterwards the resolver handler is called and the resulting value is returned to ariadne to transform into the final result object or to be used in further field resolvers.

Resolver Features:
------------------

Nesting
:::::::
When a resolver is configured as a nested resolver it can behave differently given their context. By default the abstract class does not change the behavior of the result, however when used in a model resolver it can be used to sub-filter results or look up relationships via managers and reverse names.

Federation
::::::::::

In federated graphql schemas different types are hooked up via reference parameters from decorators. Our class based resolvers allow us to easily get these parameters and use them to resolve the federated fields.

Visit Ariadne docs for more information on how to implement `Apollo Federation <https://ariadnegraphql.org/docs/apollo-federation>`_ 

~Examples~

Adding custom resolver methods

operation args
operation kwargs
reference kwargs

parent reference

Model CBR
=========
The model class based resolvers follows patterns originating from Django class based views and Django Rest Framework views. If you're familiar with them, a lot of the model based CBR class options will feel similar.

CBRs can utilize a mixin system to allow for differently configured resolvers or to create generic all in one resolvers that provide many resolver methods.


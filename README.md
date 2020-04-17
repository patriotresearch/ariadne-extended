# Ariadne Django extension

Ariadne comes with a few contrib modules to support integration with django. This module acts as additional suggestions and loaders to reduce some of the boilerplate when dealing with integrating with django models.

It copies and follows some of the conventions defined in Django Rest Framework, effort will be made to provide API compatibility with certain DRF extension modules that are relevant.

## Supported DRF modules

* Pagination classes
* Permissions classes
* Serializer classes? ( may not be needed )
* Throttling
* Django filters

## First: How to break work that has been already done into their areas of concern

Goal make re-usable modules and schema, so one doesn't have to include everything.

### `ariadne_extensions.graph`

auto schema, resolver and types loader 

Searches for `types` and `resolvers` modules as well as the `schema.graphql` defined within every installed django application.

Once found they can be used to build the final schema and resolver solution for your ariadne application.

### `ariadne_extensions.payload`
Schema, types and resolvers for the graphql `Payload` interface.

Currently the `FieldErrors` are highly coupled to django rest framework field validation exceptions.

### `ariadne_extensions.cursor_pagination`
Rename to relay_pagination maybe?

Contains the `PageInfo` graphql type and `Connection` interface for utilizing cursor based pagination.

TODO: Should we provide a input type for cursor pagination instead of just copying pagination args info paginatable list fields??

- [ ] Get rid of dependency on DRF
- [ ] Investigate the need for a serializer ( nested data reliance? )
- [ ] Organize code into multiple django apps to select desired componentry

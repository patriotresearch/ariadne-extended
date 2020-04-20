# Ariadne Django extension

Ariadne comes with a few contrib modules to support integration with django. This module acts as additional suggestions and loaders to reduce some of the boilerplate when dealing with integrating with django models.

It copies and follows some of the conventions defined in Django Rest Framework, effort will be made to provide API compatibility with certain DRF extension modules that are relevant.

The overall goal is to provide often re-used modules and GrpahQL schema, so one doesn't have to re-create them per project.

## Supported DRF modules

* Pagination classes
* Permissions classes
* Serializer classes ( may not removed and made generic )
* Throttling
* django-filters filter backend

### `ariadne_extended.graph`

auto schema, resolver and types loader 

Searches for `types` and `resolvers` modules as well as the `schema.graphql` defined within every installed django application.

Once found they can be used to build the final schema and resolver solution for your ariadne application.

### `ariadne_extended.payload`
Schema, types and resolvers for the graphql `Payload` interface.

Currently the `FieldErrors` are highly coupled to django rest framework field validation exceptions.

### `ariadne_extended.cursor_pagination`
Rename to relay_pagination maybe?

Contains the `PageInfo` graphql type and `Connection` interface for utilizing cursor based pagination.

TODO: Should we provide a input type for cursor pagination instead of just copying pagination args info paginate-able list fields??

### `ariadne_extended.filters`
Filter backend interface to pass filter arguments to django-filter

### `ariadne_extended.resolvers`
ABC for Class Based Resolvers and model resolvers that utilize DRF serializers for saving data. This is likely to change in the future.

### `ariadne_extended.uuid`
DRF UUID field scalar for use with models that may use a UUID as their primary key, or other UUID fields.

- [ ] Get rid of dependency on DRF
- [ ] Investigate the need for a serializer ( nested data reliance? )
- [x] Organize code into multiple django apps to select desired componentry
- [ ] Documentation and examples

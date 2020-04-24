import logging
from importlib import import_module
from os import path

from ariadne import load_schema_from_path
from django.apps import AppConfig
from django.apps.registry import apps

logger = logging.getLogger(__name__)


class GraphLoaderConfig(AppConfig):
    """
    Graph loader finds all the schemas, resolvers and type definitions
    """

    name = "ariadne_extended.graph_loader"

    def ready(self):
        # Find all schema.graphql and resolver modules and load them
        self.type_defs = list()
        self.types = list()
        self.resolvers = list()

        logger.debug("Trying to load resolvers and schemas:")
        for config in apps.get_app_configs():
            logger.debug("Looking at %s", config.name)

            # Schema
            self.load_schema(config)
            self.load_resolvers(config)
            self.load_custom_types(config)

        logger.debug("Types: %s", ", ".join([_type.name for _type in self.types]))

    def load_schema(self, config):
        try:
            self.type_defs.append(load_schema_from_path(path.join(config.path)))
            logger.debug("Found graphql schema")
        except FileNotFoundError:
            pass
        else:
            logger.debug("found schema in %s!", config.name)

    def load_resolvers(self, config):
        try:
            module = import_module(".resolvers", package=config.name)
            resolvers = getattr(module, "__resolvers__", None)
            if resolvers:
                self.resolvers += [getattr(module, resolver) for resolver in resolvers]
        except ModuleNotFoundError as e:
            if e.name != f"{config.name}.resolvers":
                raise e
            logger.debug("No resolvers found")
        except Exception as e:
            logger.error("Error loading types from %s", config.name)
            raise e
        else:
            logger.debug("found types in %s!", config.name)

    def load_custom_types(self, config):
        try:
            types_module = import_module(".types", package=config.name)
            for type_name in types_module.__all__:
                self.types.append(getattr(types_module, type_name))
        except ModuleNotFoundError as e:
            if e.name != f"{config.name}.types":
                raise e
            logger.debug("No types found")
        except Exception as e:
            logger.error("Error loading types from %s", config.name)
            raise e
        else:
            logger.debug("found types in %s!", config.name)


    @property
    def all_app_types(self):
        return self.types + self.resolvers

import logging
from importlib import import_module

from ariadne import EnumType, ObjectType, ScalarType, UnionType, load_schema_from_path
from django.apps import AppConfig
from django.apps.registry import apps

logger = logging.getLogger(__name__)


class GraphLoaderConfig(AppConfig):
    """
    Graph loader finds all the schemas, resolvers and type definitions in installed apps
    """

    name = "ariadne_extended.graph_loader"

    def ready(self):
        # Find all schema.graphql and resolver modules and load them
        self.type_defs = list()
        self.types = list()
        self.resolvers = list()

        logger.debug("Trying to load resolvers and schemas:")
        for config in apps.get_app_configs():
            self.load_schema(config)
            self.load_resolvers(config)
            self.load_custom_types(config)

        logger.debug("Types: %s", ", ".join([_type.name for _type in self.types]))

    def load_schema(self, config):
        try:
            schema = load_schema_from_path(config.path)
            if schema:
                self.type_defs.append(schema)
                logger.debug("found schema in %s!", config.name)
        except FileNotFoundError:
            pass

    def load_resolvers(self, config):
        try:
            module = import_module(".resolvers", package=config.name)
            resolvers = getattr(module, "__resolvers__", None)
            if resolvers:
                self.resolvers += [getattr(module, resolver) for resolver in resolvers]
        except ModuleNotFoundError as e:
            if e.name != f"{config.name}.resolvers":
                raise e
        except Exception as e:
            logger.error("Error loading types from %s", config.name)
            raise e
        else:
            logger.debug("found resolvers in %s!", config.name)

    def load_custom_types(self, config):
        try:
            types_module = import_module(".types", package=config.name)
            for type_name in [
                t
                for _, t in types_module.__dict__.items()
                if isinstance(t, ObjectType)
                or isinstance(t, ScalarType)
                or isinstance(t, EnumType)
                or isinstance(t, UnionType)
            ]:
                self.types.append(type_name)
        except ModuleNotFoundError as e:
            if e.name != f"{config.name}.types":
                raise e
        except Exception as e:
            logger.error("Error loading types from %s", config.name)
            raise e
        else:
            logger.debug("found types in %s!", config.name)

    @property
    def all_app_types(self):
        return self.types + self.resolvers

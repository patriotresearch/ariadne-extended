from ariadne_extended.permissions import AllowAny
from ariadne_extended.resolvers import ListModelResolver, Resolver, RetrieveModelMixin
from waffle import get_waffle_flag_model
from waffle.models import Sample, Switch
from waffle.utils import get_setting

from .types import query, waffle_item_interface, waffle_type


class WaffleResolver(RetrieveModelMixin, ListModelResolver):
    """
    Base resolver for waffle models, allows all users to resolve as the data is not sensitive
    and may even be resolved by users that aren't logged in.
    """

    lookup_arg = "name"
    lookup_field = "name"
    permission_classes = [AllowAny]

    def get_object(self):
        """
        Use the get method provided by the django-waffle library to lookup a flag/switch/sample

        Waffle models don't require object level permissions

        Returns an empty model class if not found with the used lookup name
        """
        lookup = self.get_lookup_filter_kwargs()
        return self.model.get(**lookup)

    def get_queryset(self):
        # Not a true QS, will ask cache for saved model objects
        return self.model.get_all()


class FlagResolver(WaffleResolver):
    model = get_waffle_flag_model()


class SwitchResolver(WaffleResolver):
    model = Switch


class SampleResolver(WaffleResolver):
    model = Sample


class AllWaffleTypesResolver(Resolver):
    def list(self, *args, **kwargs):
        return Switch.get_all() + Sample.get_all() + get_waffle_flag_model().get_all()


class ActiveResolver(Resolver):
    def check(self, parent, *args, **kwargs):
        try:
            return parent.is_active(self.request)
        except TypeError:
            return parent.is_active()


waffle_type.set_field("flags", FlagResolver.as_resolver(method="list"))
waffle_type.set_field("switches", SwitchResolver.as_resolver(method="list"))
waffle_type.set_field("samples", SampleResolver.as_resolver(method="list"))
waffle_type.set_field("all", AllWaffleTypesResolver.as_resolver(method="list"))
waffle_type.set_field("flag", FlagResolver.as_resolver(method="retrieve"))
waffle_type.set_field("switch", SwitchResolver.as_resolver(method="retrieve"))
waffle_type.set_field("sample", SampleResolver.as_resolver(method="retrieve"))
waffle_item_interface.set_field("active", ActiveResolver.as_resolver(method="check"))
query.set_field(
    "waffle",
    lambda *x: {
        "flag_default": get_setting("FLAG_DEFAULT"),
        "switch_default": get_setting("SWITCH_DEFAULT"),
        "sample_default": get_setting("SAMPLE_DEFAULT"),
        "flagDefault": get_setting("FLAG_DEFAULT"),
        "switchDefault": get_setting("SWITCH_DEFAULT"),
        "sampleDefault": get_setting("SAMPLE_DEFAULT"),
    },
)

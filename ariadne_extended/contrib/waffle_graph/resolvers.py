from ariadne_extended.resolvers import ListModelResolver, Resolver
from waffle import get_waffle_flag_model
from waffle.models import Sample, Switch
from waffle.utils import get_setting

from .types import query, waffle_item_interface, waffle_type


class WaffleResolver(ListModelResolver):
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


@waffle_item_interface.field("active")
def resolve_flag_active(obj, info, *args, **kwargs):
    try:
        return obj.is_active(info.context)
    except TypeError:
        return obj.is_active()


waffle_type.set_field("flags", FlagResolver.as_resolver(method="list"))
waffle_type.set_field("switches", SwitchResolver.as_resolver(method="list"))
waffle_type.set_field("samples", SampleResolver.as_resolver(method="list"))
waffle_type.set_field("all", AllWaffleTypesResolver.as_resolver(method="list"))
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

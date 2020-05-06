from ariadne import InterfaceType, ObjectType, QueryType

waffle_type = ObjectType("Waffle")
waffle_flag_type = ObjectType("WaffleFlag")
waffle_switch_type = ObjectType("WaffleSwitch")
waffle_sample_type = ObjectType("WaffleSample")
waffle_item_interface = InterfaceType("WaffleItem")
query = QueryType()


def resolve_waffle_type(obj, *args):
    return f"Waffle{obj.__class__.__name__}"


waffle_item_interface.set_type_resolver(resolve_waffle_type)

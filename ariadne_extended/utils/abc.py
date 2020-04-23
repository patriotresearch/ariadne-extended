def concreter(abclass):
    class concreteCls(abclass):
        pass

    concreteCls.__abstractmethods__ = frozenset()
    return type("DummyConcrete" + abclass.__name__, (concreteCls,), {})

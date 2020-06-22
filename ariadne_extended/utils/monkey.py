def patch_autoreload():
    """
    Monkey patches Django's autoreload file finder to pickup and trigger when graphql files
    are added or changed.

    Only for development use, intended to be called before running main() in your manage.py.
    """
    try:
        import django.utils.autoreload
    except Exception:
        return
    from glob import glob
    from itertools import chain
    from pathlib import Path

    old_iter = django.utils.autoreload.iter_all_python_module_files

    def new_iter():
        results = old_iter()
        graphql_files = map(Path, glob("**/**/*.graphql"))
        return frozenset(chain(results, graphql_files))

    django.utils.autoreload.iter_all_python_module_files = new_iter

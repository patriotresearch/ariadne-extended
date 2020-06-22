=====
Usage
=====

To use Ariadne Extended in a project::

    import ariadne_extended


To make `./manage.py runserver` aware of graphql file changes just modify your `./manage.py` script like so::

    if __name__ == '__main__':
        from ariadne_extended.utils.monkey import patch_autoreload
        patch_autoreload()
        main()

This will monkey patch Django's built-in autoreload functionality to watch for changes to all `*.graphql` files
within your project directory. Only intended to be used for development purposes!

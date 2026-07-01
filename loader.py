import importlib
import inspect
import pkgutil

import sites


def load_sites():

    loaded = []

    for _, module_name, _ in pkgutil.iter_modules(sites.__path__):

        module = importlib.import_module(
            f"sites.{module_name}"
        )

        for _, cls in inspect.getmembers(
            module,
            inspect.isclass
        ):

            if cls.__module__ == module.__name__:

                loaded.append(cls())

    return loaded

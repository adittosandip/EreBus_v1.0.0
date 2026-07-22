import importlib
import inspect
import pkgutil

import sites

from core.base import BaseSite


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

            if (
                cls.__module__ == module.__name__
                and issubclass(cls, BaseSite)
                and cls is not BaseSite
            ):

                loaded.append(cls())

    return loaded

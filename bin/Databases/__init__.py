"""
Package for databases, which can include connector to different databases
"""
__pdoc__ = {}
__pdoc__[".__pycache__"] = False
__pdoc__[".__init__"] = False


from inspect import isclass
from pkgutil import iter_modules
from importlib import import_module
import os

from Databases.database import Database

package_dir = os.path.dirname(os.path.abspath(__file__))
for (_, module_name, _) in iter_modules([package_dir]):

    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute) and issubclass(attribute, Database):
            globals()[attribute_name] = attribute
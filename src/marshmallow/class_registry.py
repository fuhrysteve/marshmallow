"""A registry of :class:`Schema <marshmallow.Schema>` classes. This allows for string
lookup of schemas, which may be used with
class:`fields.Nested <marshmallow.fields.Nested>`.

.. warning::

    This module is treated as private API.
    Users should not need to use this module directly.
"""
from marshmallow.exceptions import RegistryError

# {
#   <class_name>: <list of class objects>
#   <module_path_to_class>: <list of class objects>
# }
_registry = {}


def register(classname, cls):
    """Add a class to the registry of serializer classes. When a class is
    registered, an entry for both its classname and its full, module-qualified
    path are added to the registry.

    Example: ::

        class MyClass:
            pass

        register('MyClass', MyClass)
        # Registry:
        # {
        #   'MyClass': [path.to.MyClass],
        #   'path.to.MyClass': [path.to.MyClass],
        # }

    """
    # Module where the class is located
    module = cls.__module__
    # Full module path to the class
    # e.g. user.schemas.UserSchema
    fullpath = ".".join([module, classname])
    # If the class is already registered; need to check if the entries are
    # in the same module as cls to avoid having multiple instances of the same
    # class in the registry
    if classname in _registry and not any(
        each.__module__ == module for each in _registry[classname]
    ):
        _registry[classname].append(cls)
    elif classname not in _registry:
        _registry[classname] = [cls]

    # Also register the full path
    if fullpath not in _registry:
        _registry.setdefault(fullpath, []).append(cls)
    else:
        # If fullpath does exist, replace existing entry
        _registry[fullpath] = [cls]
    return None


def get_class(classname, all=False):
    """Retrieve a class from the registry.

    :raises: marshmallow.exceptions.RegistryError if the class cannot be found
        or if there are multiple entries for the given class name.
    """
    try:
        classes = _registry[classname]
    except KeyError:
        raise RegistryError(
            "Class with name {!r} was not found. You may need "
            "to import the class.".format(classname)
        )
    if len(classes) > 1:
        if all:
            return _registry[classname]
        raise RegistryError(
            "Multiple classes with name {!r} "
            "were found. Please use the full, "
            "module-qualified path.".format(classname)
        )
    else:
        return _registry[classname][0]

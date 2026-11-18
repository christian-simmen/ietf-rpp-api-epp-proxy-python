import importlib

from registration.extension_registry import ExtensionRegistry


def load_extensions(module_paths) -> ExtensionRegistry:
    """Imports each module the configuration names (`rpp_extensions`) and lets it register its parts. A module that
    cannot be imported, or has no `register`, stops the app: a deployment never runs without an extension it names."""
    registry = ExtensionRegistry()
    for path in module_paths or ():
        try:
            module = importlib.import_module(path)
        except ImportError as e:
            raise ValueError(f"rpp_extensions: cannot import {path!r}: {e}") from e
        register = getattr(module, "register", None)
        if not callable(register):
            raise ValueError(f"rpp_extensions: {path!r} has no register(registry)")
        register(registry)
    return registry

import functools
import inspect

from dataclasses import dataclass
from typing import Dict, Callable
from pythia.plugin.hooks import HookType, HookPayload

"""
A function that is registered as a plugin hook.
The first argument is the hook payload;
The second argument is the global Pythia configuration;
"""
HookFn = Callable[[HookPayload, Dict], None]


@dataclass
class HookFnEntry:
    """Represents a hook registered by a plugin."""

    def __init__(self, fun: HookFn, plugin: str, hook_type: HookType):
        self.fun = fun
        self.plugin = plugin
        self.hook_type = hook_type


"""A function that registers a hook into the plugin system."""
HookRegisterer = Callable[[HookType, HookFn], HookFnEntry]

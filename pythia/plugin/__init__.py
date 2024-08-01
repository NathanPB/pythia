import inspect
import logging
import sys

from abc import ABC, abstractmethod
from importlib import import_module
from importlib.util import find_spec
from typing import Dict, List, Type
from pythia.plugin.hooks import HookType, HookPayload
from pythia.plugin.types import HookFnEntry, HookRegisterer, HookFn
from pythia.plugin.exceptions import HookNotificationException, PluginInitializationException


class PythiaPlugin(ABC):
    """Defines the plugin lifecycle functions"""

    @abstractmethod
    def initialize(
            self,
            pythia_config: Dict,
            plugin_config: Dict,
            hook_registerer: HookRegisterer,
            logger: logging.Logger
    ):
        """Function called when the plugin is initialized."""
        pass


class PluginManager:
    """Loads plugins, manages their hooks registration and lifecycle"""

    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.hooks: Dict[HookType, List[HookFnEntry]] = {}
        self.loaded_plugins: List[str] = []
        self._load_plugins()

    def create_hook_registerer(self, plugin: str) -> HookRegisterer:
        """
        Creates a HookRegisterer for the given plugin.
        """

        def register_hook(hook_type: HookType, fun: HookFn) -> HookFnEntry:
            # Important to note that this is a higher-order function.

            if hook_type not in self.hooks:
                self.hooks[hook_type] = []

            hook_entry = HookFnEntry(fun, plugin, hook_type)
            self.hooks[hook_type].append(hook_entry)
            self.logger.info(f"Registered plugin hook {hook_entry}")
            return hook_entry

        return register_hook

    def notify_hook(self, payload: HookPayload) -> None:
        """Notifies registered hooks of an event."""
        hook_entries = self.hooks.get(type(payload), [])
        for hook_entry in hook_entries:
            try:
                hook_entry.fun(payload, self.config)
            except Exception as e:
                raise HookNotificationException(hook_entry, e)

    def _load_plugins(self) -> None:
        """
        Searches for plugin definitions in the configuration file and attempts to load them,
         using the `self._load_plugin` method.
        """

        if not self.config.get("plugins", []):
            self.logger.info("No plugins to load")
            return

        self.logger.info("Loading plugins...")

        for plugin_def in self.config["plugins"]:
            if not isinstance(plugin_def, dict) or type(plugin_def.get("plugin", None)) != str:
                self.logger.warning(f"Skipping invalid plugin configuration: {plugin_def}")
                continue

            if plugin_def["plugin"] in self.loaded_plugins:
                self.logger.warning(
                    f"Skipping plugin {plugin_def['plugin']} because"
                    " a plugin with the same scope has already been loaded"
                )
                continue

            self._load_plugin(plugin_def)
            self.loaded_plugins.append(plugin_def["plugin"])

    def _load_plugin(self, plugin_def: Dict) -> None:
        """
        Attempts to load the given plugin definition (as defined in the configuration file).
        """
        plugin = plugin_def["plugin"]
        self.logger.info(f"Loading plugin {plugin}...")

        spec = find_spec(f"pythia.plugins.{plugin}")
        if spec is None:
            self.logger.warning(f"Cannot find plugin: {plugin}")
            return

        plugin_class = self._load_plugin_class(plugin)
        if plugin_class is None:
            self.logger.warning(f"Plugin {plugin} does not have a valid entrypoint")
            return

        try:
            hook_registerer = self.create_hook_registerer(plugin)
            plugin_instance = plugin_class()
            plugin_logger = self.logger.getChild(plugin)
            plugin_instance.initialize(self.config, plugin_def, hook_registerer, plugin_logger)
        except Exception as e:
            self.logger.error(f"Plugin {plugin} crashed on initialization")
            raise PluginInitializationException(plugin, e)

    def _load_plugin_class(self, plugin: str) -> Type[PythiaPlugin] | None:
        """
        Loads the given plugin to the runtime and returns the entrypoint class.
        """
        loaded = import_module(f"pythia.plugins.{plugin}")
        classes = inspect.getmembers(loaded, inspect.isclass)

        for _, class_obj in classes:
            if issubclass(class_obj, PythiaPlugin) and class_obj is not PythiaPlugin:
                if class_obj.__module__ == loaded.__name__:
                    return class_obj
        return None

from pythia.plugin.types import HookFnEntry


class PluginInitializationException(BaseException):
    """
    Exception raised when a plugin fails to initialize.
    """
    def __init__(self, plugin: str, cause: BaseException):
        super().__init__(cause)
        self.message = f"Plugin {plugin} failed to initialize: {cause}"


class HookNotificationException(BaseException):
    """
    Exception raised when a hook registered by a plugin crashes.
    """
    def __init__(self, hook_entry: HookFnEntry, cause: BaseException):
        super().__init__(cause)
        self.message = f"Hook {hook_entry} crashed: {cause}"

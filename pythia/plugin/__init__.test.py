import logging
import sys
import unittest

from pythia.plugin import PluginManager
from pythia.plugin.exceptions import PluginInitializationException, HookNotificationException
from pythia.plugin.hooks import PostConfigHookPayload, PostBuildContextHookPayload, \
    PostPeerlessPixelSuccessHookPayload, PostPeerlessPixelSkipHookPayload, \
    PostRunPixelSuccessHookPayload, PostRunPixelFailedHookPayload


def make_config(raise_init=False, raise_hook=False):
    return {
        "plugins": [
            {
                "plugin": "test_plugin",
                "params": {"raise_init": raise_init, "raise_hook": raise_hook}
            }
        ]
    }


class PluginManagerTest(unittest.TestCase):
    logger = logging.getLogger("PluginManagerTest")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def test_PluginLoading(self):
        manager = PluginManager(make_config(), self.logger)
        self.assertEqual(len(manager.loaded_plugins), 1)
        self.assertEqual(manager.loaded_plugins[0], "test_plugin")

    def test_HookRegistration(self):
        manager = PluginManager(make_config(), self.logger)
        self.assertEqual(list(manager.hooks.keys()), [
            PostConfigHookPayload,
            PostBuildContextHookPayload,
            PostPeerlessPixelSuccessHookPayload,
            PostPeerlessPixelSkipHookPayload,
            PostRunPixelSuccessHookPayload,
            PostRunPixelFailedHookPayload
        ])

    def test_HookRegistrationDuplicate(self):
        manager = PluginManager(make_config(), self.logger)
        self.assertEqual(len(manager.hooks[PostConfigHookPayload]), 2)

    def test_HookNotification(self):
        manager = PluginManager(make_config(), self.logger)

        ctx = {"incrementing": 0}
        manager.notify_hook(PostBuildContextHookPayload(ctx))
        self.assertEqual(ctx["incrementing"], 1)
        manager.notify_hook(PostBuildContextHookPayload(ctx))
        self.assertEqual(ctx["incrementing"], 2)

    def test_PluginInitializationException(self):
        with self.assertRaises(PluginInitializationException):
            PluginManager(make_config(raise_init=True), self.logger)

    def test_HookNotificationException(self):
        with self.assertRaises(HookNotificationException):
            config = make_config(raise_hook=True)
            manager = PluginManager(config, self.logger)
            manager.notify_hook(PostConfigHookPayload(config))

if __name__ == '__main__':
    unittest.main()

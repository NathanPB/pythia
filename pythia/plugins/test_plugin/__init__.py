from logging import Logger
from typing import Dict
from pythia.plugin import PythiaPlugin, HookRegisterer
from pythia.plugin.hooks import PostConfigHookPayload, PostBuildContextHookPayload, \
    PostPeerlessPixelSuccessHookPayload, PostPeerlessPixelSkipHookPayload, \
    PostRunPixelSuccessHookPayload, PostRunPixelFailedHookPayload


class TestPluginEntryPoint(PythiaPlugin):
    logger: Logger

    def initialize(
            self,
            pythia_config: Dict,
            plugin_config: Dict,
            hook_registerer: HookRegisterer,
            logger: Logger
    ):
        self.logger = logger

        self.logger.info("Initializing plugin")
        hook_registerer(PostConfigHookPayload, self.sample_function)
        hook_registerer(PostConfigHookPayload, self.duplicate_hook)
        hook_registerer(PostBuildContextHookPayload, self.contexted_function)
        hook_registerer(PostPeerlessPixelSuccessHookPayload, self.on_peerless_success)
        hook_registerer(PostPeerlessPixelSkipHookPayload, self.on_peerless_skip)
        hook_registerer(PostRunPixelSuccessHookPayload, self.on_run_pixel_success)
        hook_registerer(PostRunPixelFailedHookPayload, self.on_run_pixel_failed)

        # Demonstration of what happens when the plugin crashes on initialization
        if plugin_config["params"].get("raise_init", False):
            raise Exception("Testing plugin exception")

        # Demonstration of what happens when a plugin hook crashes
        if plugin_config["params"].get("raise_hook", False):
            hook_registerer(PostConfigHookPayload, self.problematic_hook)

    def sample_function(self, payload: PostConfigHookPayload, config: Dict) -> None:
        self.logger.info("Running the sample_function()")
        config["sample_value"] = 1

    def duplicate_hook(self, payload: PostConfigHookPayload, config: Dict) -> None:
        self.logger.info("PostConfigHookPayload was registered twice, no problems :)")

    def contexted_function(self, payload: PostBuildContextHookPayload, config: Dict) -> None:
        self.logger.info("Running the contexted_function()")
        payload.context["incrementing"] = payload.context.get("incrementing", 0) + 1

    def on_peerless_success(self, payload: PostPeerlessPixelSuccessHookPayload, config: Dict) -> None:
        self.logger.info("peerless success")

    def on_peerless_skip(self, payload: PostPeerlessPixelSkipHookPayload, config: Dict) -> None:
        self.logger.info("peerless skip")

    def on_run_pixel_success(self, payload: PostRunPixelSuccessHookPayload, config: Dict) -> None:
        self.logger.info("run pixel success")

    def on_run_pixel_failed(self, payload: PostRunPixelFailedHookPayload, config: Dict) -> None:
        self.logger.info("run pixel failed")

    def problematic_hook(self, payload: PostConfigHookPayload, config: Dict) -> None:
        raise Exception("Testing plugin exception")

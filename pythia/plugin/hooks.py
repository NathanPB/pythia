from dataclasses import dataclass
from abc import ABC
from typing import Dict, Type, List

# TODO implement hooks that are commented out


class HookPayload(ABC):
    """Base class for all plugin hook payloads. Every further payload should inherit from this class."""
    pass


HookType = Type[HookPayload]


@dataclass
class PostConfigHookPayload(HookPayload):
    """Hook called after the configuration is loaded."""
    config: Dict


# @dataclass
# class PreBuildContextHookPayload(HookPayload):
#     """Hook called before the context is built."""
#     context: Dict


@dataclass
class PostBuildContextHookPayload(HookPayload):
    """Hook called after the context is built."""
    context: Dict


@dataclass
class PostPeerlessPixelSuccessHookPayload(HookPayload):
    """Hook called after a peerless pixel is successfully run."""
    context: Dict
    args: {"run": Dict, "config": Dict, "ctx": Dict}


@dataclass
class PostPeerlessPixelSkipHookPayload(HookPayload):
    """Hook called after a peerless pixel is skipped."""
    args: {"run": Dict, "config": Dict, "ctx": Dict}


@dataclass
class PostComposePeerlessPixelSuccessHookPayload(HookPayload):
    """Hook called after a peerless pixel is successfully composed."""
    context: Dict


@dataclass
class PostComposePeerlessPixelSkipHookPayload(HookPayload):
    """Hook called after a peerless pixel is skipped."""


@dataclass
class PostComposePeerlessAllHookPayload(HookPayload):
    """Hook called after all peerless pixels are composed."""
    run_list: List[str]


# @dataclass
# class PostSetupHookPayload(HookPayload):
#     """Hook called after the setup is complete."""
#     context: Dict


@dataclass
class PreRunHookPayload(HookPayload):
    """Hook called before a run is run."""
    context: Dict


# @dataclass
# class RunPixelHookPayload(HookPayload):
#     """Hook called after a run is run."""
#     context: Dict


@dataclass
class PostRunPixelSuccessHookPayload(HookPayload):
    """Hook called after a DSSAT execution completed successfully."""
    details: Dict
    out: bytes
    err: bytes
    code: int


@dataclass
class PostRunPixelFailedHookPayload(HookPayload):
    """Hook called after a DSSAT execution failed."""
    details: Dict
    out: bytes
    err: bytes
    code: int


@dataclass
class PostRunAllHookPayload(HookPayload):
    """Hook called after all runs are run."""
    run_list: List[{"dir": str, "file": str}]


@dataclass
class PreAnalyticsHookPayload(HookPayload):
    """Hook called before analytics are run."""


@dataclass
class PostAnalyticsHookPayload(HookPayload):
    """Hook called after analytics are run."""
    run_outputs: List[str]
    calculated: List[str]
    filtered: List[str]


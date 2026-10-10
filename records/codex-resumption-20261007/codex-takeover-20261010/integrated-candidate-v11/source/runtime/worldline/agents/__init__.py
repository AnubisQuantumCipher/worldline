from __future__ import annotations

from typing import Callable

from .base import AgentAdapter
from .claude import ClaudeAdapter
from .codex import CodexAdapter
from .generic import GenericAdapter
from .omp import OmpAdapter
from .pi import PiAdapter
from ..config import GlobalConfig
from ..errors import WorldlineError

_BUILTINS: dict[str, Callable[[], AgentAdapter]] = {
    "codex": CodexAdapter,
    "claude": ClaudeAdapter,
    "omp": OmpAdapter,
    "pi": PiAdapter,
}


def adapter(name: str, config: GlobalConfig) -> AgentAdapter:
    factory = _BUILTINS.get(name)
    if factory is not None:
        instance = factory()
        instance.extra_argv = config.adapter_argv(name)
        return instance
    return GenericAdapter(config.generic_agent(name))


def adapter_names(config: GlobalConfig) -> list[str]:
    return sorted({*_BUILTINS, *config.value["agentCommands"]})

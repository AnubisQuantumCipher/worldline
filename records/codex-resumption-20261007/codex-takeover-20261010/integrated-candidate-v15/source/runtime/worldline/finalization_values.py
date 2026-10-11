"""Lossless values for the additive finalization dependency.

These values are observations, not authenticity or permission claims. A Start
has no content field. The immutable input is captured after legitimate agent
edits; its final config/repository components need not equal the initial ones.
"""
from __future__ import annotations

from dataclasses import dataclass
from .evaluation_wire import OwnedRecord


@dataclass(frozen=True)
class StartValue:
    store_id: bytes
    subject: bytes
    run: bytes
    epoch: bytes
    requirement: bytes | None
    policy: bytes
    verifier_plan: bytes
    base_context: bytes
    parent: bytes
    config: bytes
    repository: bytes
    required: tuple[tuple[bytes, bytes], ...]
    declaration: str


@dataclass(frozen=True)
class InputValue:
    start: StartValue
    root: bytes
    manifests: bytes
    filesystem: bytes
    config: bytes
    repository: bytes


@dataclass(frozen=True)
class UnsealedResult:
    start: StartValue
    check: bytes
    source: bytes
    execution: bytes | None
    verifier: bytes | None
    state: str
    outcome: str | None
    payload: bytes
    declared: bytes
    wire: OwnedRecord


@dataclass(frozen=True)
class CaptureValue:
    start: StartValue
    input: InputValue
    post_root: bytes
    post_manifests: bytes
    context: bytes
    source: bytes
    results: tuple[UnsealedResult, ...]
    completion: tuple[bytes, bytes]


@dataclass(frozen=True)
class ComponentsValue:
    environment: bytes
    evidence: bytes


@dataclass(frozen=True)
class SealValue:
    capture: CaptureValue
    content: bytes
    components: ComponentsValue
    evidence: bytes
    environment: bytes


@dataclass(frozen=True)
class ClassifiedValue:
    state: str
    outcome: str | None
    promotion: bool


@dataclass(frozen=True)
class SealedValue:
    value: SealValue
    identity: bytes
    classification: ClassifiedValue
    # These are the native summary, not a Python reclassification.
    finalization_state: str
    finalization_outcome: str | None

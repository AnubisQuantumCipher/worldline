"""Same raw observation mapping as the retained classifier producer.
Translation/provenance are required boundary obligations, not proved by this copy.
"""
from typing import Mapping, Any
from .core import EvaluationFacts
from .finalize import stopped_supervision

def observations(result: Mapping[str, Any]) -> EvaluationFacts:
    executed = result.get("executedVerifierSet")
    status = result.get("status")
    channel_value = result.get("resultChannel")
    channel = channel_value if isinstance(channel_value, Mapping) else {}
    exit_code = result.get("exitCode")
    supervision_value = result.get("supervision")
    supervision = supervision_value if isinstance(supervision_value, Mapping) else {}
    channel_kind = (
        "ABSENT" if channel_value is None else
        "MALFORMED" if not isinstance(channel_value, Mapping) else
        "EMPTY" if not channel else
        "ACCEPTED" if channel.get("accepted") is True else
        "REJECTED" if channel.get("accepted") is False else "OTHER"
    )
    stage = channel.get("stage")
    supervisor_kind = supervision.get("kind")
    facts = EvaluationFacts(
        source=result.get("origin") if result.get("origin") in ("engine", "agent") else "external",
        status=status if status in ("PASS", "FAIL", "UNASSESSED") else
               ("ABSENT" if status is None else "OTHER"),
        channel=channel_kind,
        stage=stage if stage in ("SANDBOX_NEVER_STARTED", "STOPPED_BY_MANAGER",
                                 "HARNESS_SIGNALLED") else
              ("ABSENT" if stage is None else "OTHER"),
        exit_present=exit_code is not None,
        # bool is an int subclass; True is not an exit status.
        exit_integer=type(exit_code) is int,
        supervisor=supervisor_kind if supervisor_kind in ("SUPERVISED", "STOPPED") else
                   ("ABSENT" if supervisor_kind is None else "OTHER"),
        supervisor_stopped=stopped_supervision(supervision),
        # An empty or malformed bundle record is present and unverifiable, not absent.
        bundle_present=executed is not None,
        bundle_is_mapping=isinstance(executed, Mapping),
        bundle_stable=isinstance(executed, Mapping) and executed.get("stable") is True,
        bundle_changed=isinstance(executed, Mapping) and bool(executed.get("changedDuringExecution")),
        unsatisfied_imports=isinstance(executed, Mapping) and bool(executed.get("unsatisfiedImports")),
    )
    return facts

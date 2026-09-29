from __future__ import annotations

import base64
import binascii
import hashlib
import time

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from typing import Any, Mapping, Sequence

from .canonical import atomic_write_json
from .core import Core, EvaluationFacts, EvidencePresence
from .delta import Delta
from .environment import EnvironmentCapture, OwnedProcess, capture_dependencies, evidence_manifest
from .project import protected_matches
from .model import utc_now
from .errors import WorldlineError
from .linux.docker import DockerAdapter
from .linux.git import GitAdapter
from .linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from .manifest import CapturedManifest, Manifest
from .model import World, WorldState
from .paths import WorldlinePaths, secure_directory
from .report import MAX_REPORT_BYTES
from .store import StateStore
from .trusted import trusted_inline

_COPY_SCRIPT = """
import os
import subprocess
import shutil
import sys
for index in range(1, len(sys.argv), 2):
    source = sys.argv[index]
    destination = sys.argv[index + 1]
    os.makedirs(destination, mode=0o700, exist_ok=False)
    subprocess.run(['/usr/bin/cp', '--archive', '--reflink=auto', source + '/.', destination], check=True)
    shutil.copystat(source, destination, follow_symlinks=False)
""".strip()


@dataclass(frozen=True)
class CandidateSnapshot:
    """Daemon-owned input copied before checks; check outputs live elsewhere.

    This identifies the starting tree of a mutable evaluation overlay. It does not prove
    that an examiner kept that overlay unchanged while it ran.
    """

    world_instance: str
    directory: Path
    manifests: Mapping[str, CapturedManifest]
    root_hash: str

    def binding(self) -> dict[str, Any]:
        return {
            "worldInstance": self.world_instance,
            "rootSetHash": self.root_hash,
            "rootManifests": {key: value.root_hash for key, value in sorted(self.manifests.items())},
            "role": "pre-check-input",
        }


def stopped_supervision(supervision: Mapping[str, Any]) -> bool:
    """The manager stopped the unit (timeout, cancel) rather than letting it exit on its own."""
    return bool(supervision.get("stoppedByManager")) or supervision.get("result") == "stopped"


def _private_role_observed(observation: Any, role: str) -> bool:
    if not isinstance(observation, Mapping) or type(role) is not str:
        return False
    expected = {"examiner": 0, "worker": 1, "candidate": 2}.get(role)
    if expected is None:
        return False
    status, namespaces = observation.get("status"), observation.get("namespaces")
    if not isinstance(status, Mapping) or not isinstance(namespaces, Mapping):
        return False
    if (observation.get("role") != role
            or type(observation.get("uid")) is not int or observation["uid"] != expected
            or type(observation.get("gid")) is not int or observation["gid"] != expected
            or status.get("NoNewPrivs") != "1" or status.get("Groups") != ""
            or observation.get("reportMounted") is not (role == "examiner")
            or observation.get("brokerMounted") is not (role == "examiner")
            or observation.get("workerBrokerMounted") is not (role == "worker")):
        return False
    for key in ("CapEff", "CapPrm", "CapBnd", "CapAmb"):
        value = status.get(key)
        if not isinstance(value, str) or re.fullmatch(r"0+", value) is None:
            return False
    for key in ("Uid", "Gid"):
        value = status.get(key)
        if not isinstance(value, str) or value.split() != [str(expected)] * 4:
            return False
    for key in ("pid", "mnt", "user"):
        value = namespaces.get(key)
        if not isinstance(value, str) or re.fullmatch(key + r":\[[0-9]+\]", value) is None:
            return False
    return True


def _private_report_verified(result: Mapping[str, Any], *, execution: str, integrity: str) -> bool:
    """Verify report provenance for either a completed passing or failing examination.

    Labels alone confer no authority. The producer must establish these facts before building
    the result; persisted evidence is bound and rechecked again at promotion.
    """
    if (result.get("profile") != "private-evaluator-v1" or result.get("origin") != "supervisor"
            or execution != "COMPLETED" or integrity != "VERIFIED"
            or type(result.get("exitCode")) is not int or result["exitCode"] < 0):
        return False
    channel, supervision = result.get("resultChannel"), result.get("supervision")
    boundary, report = result.get("evaluatorBoundary"), result.get("privateReport")
    snapshot, executed = result.get("candidateSnapshot"), result.get("executedVerifierSet")
    if any(not isinstance(value, Mapping) for value in
           (channel, supervision, boundary, report, snapshot, executed)):
        return False
    if (channel.get("accepted") is not True
            or channel.get("recordProducer") != "daemon-outside-sandbox"
            or supervision.get("kind") != "SUPERVISED" or supervision.get("started") is not True
            or supervision.get("stoppedByManager") is not False
            or supervision.get("result") != ("success" if result["exitCode"] == 0 else "failure")
            or type(supervision.get("launcherExit")) is not int
            or supervision["launcherExit"] != result["exitCode"]
            or supervision.get("exitCode") not in (None, "exited")
            or (supervision.get("exitStatus") is not None
                and (type(supervision["exitStatus"]) is not int
                     or supervision["exitStatus"] != result["exitCode"]))
            or boundary.get("profileId") != result["profile"]
            or ("error" in boundary and boundary["error"] is not None)
            or type(boundary.get("examinerReturnCode")) is not int
            or boundary["examinerReturnCode"] != result["exitCode"]
            or type(boundary.get("bootstrapExitCode")) is not int
            or boundary["bootstrapExitCode"] != result["exitCode"]
            or not isinstance(boundary.get("managerBootstrapProperties"), Mapping)
            or boundary["managerBootstrapProperties"].get("NoNewPrivileges") != "no"
            or boundary.get("rolesCompleted") is not True or boundary.get("reportMountExclusive") is not True
            or report.get("collection") != "private-directory"):
        return False
    for report_key, expected in (
            ("runId", boundary.get("runId")), ("checkId", result.get("id")),
            ("candidateIdentity", snapshot.get("rootSetHash")),
            ("verifierIdentity", executed.get("identity"))):
        if (not isinstance(expected, str) or not expected or "\x00" in expected
                or report.get(report_key) != expected):
            return False
    digest = report.get("sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        return False
    if type(report.get("sizeBytes")) is not int or not 0 < report["sizeBytes"] <= MAX_REPORT_BYTES:
        return False
    payload_b64 = report.get("payloadB64")
    if (not isinstance(payload_b64, str)
            or len(payload_b64) > ((MAX_REPORT_BYTES + 2) // 3) * 4):
        return False
    try:
        payload = base64.b64decode(payload_b64, validate=True)
    except (binascii.Error, ValueError):
        return False
    if len(payload) != report["sizeBytes"] or hashlib.sha256(payload).hexdigest() != digest:
        return False
    examiner, workers = boundary.get("examiner"), boundary.get("workers")
    if not _private_role_observed(examiner, "examiner") or not isinstance(workers, list):
        return False
    worker_roles = []
    candidate_roles = []
    for worker in workers:
        if not isinstance(worker, Mapping) or type(worker.get("returncode")) is not int:
            return False
        observation = worker.get("observation")
        role = worker.get("principal", "worker")
        if not _private_role_observed(observation, role) or role not in ("worker", "candidate"):
            return False
        if (observation["namespaces"]["user"] != examiner["namespaces"]["user"]
                or any(observation["namespaces"][key] == examiner["namespaces"][key]
                       for key in ("pid", "mnt"))
                or observation.get("uidMap") != examiner.get("uidMap")
                or observation.get("gidMap") != examiner.get("gidMap")):
            return False
        (worker_roles if role == "worker" else candidate_roles).append(observation)
    for candidate in candidate_roles:
        for worker in worker_roles:
            # Earlier role namespaces may have exited and the kernel can reuse
            # their namespace inode numbers. Identity separation is the stable
            # cross-run fact; live namespace separation is checked by bootstrap.
            if candidate["uid"] == worker["uid"] or candidate["gid"] == worker["gid"]:
                return False
    return True


@dataclass(frozen=True)
class CheckDeclaration:
    """What the policy in force declares a required check to be: the format and evaluator
    profile it must have run as, and whether a verifier bundle is declared for it (which then
    must be named as what executed).

    Built from the requirement record -- the policy and its resolved verifier list -- and never
    from a check result, so the kernel's Declaration_Matches compares two sources.
    """

    format: str | None
    profile: str | None
    bundle_declared: bool
    # WORLDLINE's own results are identified by origin and carry no profile (1.9.0); a policy
    # check's record must state its profile and is not constrained by origin.
    origin: str | None = None


# Results WORLDLINE produces itself rather than from a policy check. Their ids are reserved in
# project configs, so a policy cannot declare a check that shadows one.
ENGINE_DECLARATIONS: dict[str, CheckDeclaration] = {
    "agent": CheckDeclaration("exit", None, False, origin="agent"),
    "protected-paths": CheckDeclaration("engine", None, False, origin="engine"),
}


def runner_agent_record(record: Any) -> tuple[Any, bool]:
    """The agent record as the kernel should read it, and whether a legacy shape was mapped.

    Runners before 1.5.0 wrote the agent's own record without `origin`, and a missing origin is
    classified as an external result, which such a record can never complete as. That record
    is recognised by the exact shape only the runner produced -- id `agent`, kind `build`, format
    `exit`, a supervision mapping and a raw-event hash, with no result channel and no verifier
    bundle -- and read as origin `agent`. The kernel's agent branch still requires a supervised,
    unstopped run with an integer exit. Anything else is passed through unchanged.
    """
    if (isinstance(record, Mapping) and record.get("id") == "agent" and "origin" not in record
            and record.get("kind") == "build" and record.get("format") == "exit"
            and "resultChannel" not in record and "executedVerifierSet" not in record
            and isinstance(record.get("supervision"), Mapping) and "rawEventHash" in record):
        return {**record, "origin": "agent"}, True
    return record, False


def check_declarations(requirement: Mapping[str, Any] | None) -> dict[str, CheckDeclaration]:
    """Per-check declarations from a requirement record (`requirements()`/`current_requirements()`).

    A missing or malformed requirement yields no declarations, and a check with no declaration
    is never admitted: the absence is carried to the kernel as Declaration_Matches = False.
    """
    if not isinstance(requirement, Mapping):
        return {}
    policy = requirement.get("policy")
    canonical = policy.get("canonical") if isinstance(policy, Mapping) else None
    if not isinstance(canonical, Mapping):
        return {}
    bundles = {
        str(entry.get("checkId"))
        for entry in (requirement.get("verifiers") or ())
        if isinstance(entry, Mapping) and entry.get("checkId") is not None
    }
    declared: dict[str, CheckDeclaration] = {}
    for item in canonical.get("checks") or ():
        if isinstance(item, Mapping) and isinstance(item.get("id"), str) and item["id"]:
            # The canonical policy always states the profile (validation.canonical_checks); a
            # check without one has no declaration rather than a defaulted one (1.9.0).
            profile = item.get("profile")
            if not isinstance(profile, str) or not isinstance(item.get("format"), str):
                continue
            declared[item["id"]] = CheckDeclaration(item["format"], profile, item["id"] in bundles)
    if canonical.get("protected"):
        declared["protected-paths"] = ENGINE_DECLARATIONS["protected-paths"]
    return declared


def required_roster(requirement: Mapping[str, Any] | None) -> tuple[list[str], bool]:
    """The promotion roster a requirement record imposes, and whether an empty one was declared.

    Required policy checks plus the engine's protected-paths check when the policy protects any
    path. An empty roster counts as declared only when a policy file was actually read
    (`sourceSha256` present); a project with no policy has declared nothing, and nothing is not
    a pass.
    """
    policy = requirement.get("policy") if isinstance(requirement, Mapping) else None
    if not isinstance(policy, Mapping):
        return [], False
    required = sorted({str(item) for item in (policy.get("requiredChecks") or ())})
    canonical = policy.get("canonical")
    if isinstance(canonical, Mapping) and canonical.get("protected") and "protected-paths" not in required:
        required.append("protected-paths")
    return required, isinstance(policy.get("sourceSha256"), str) and bool(policy.get("sourceSha256"))


def _declaration_matches(result: Mapping[str, Any], declared: CheckDeclaration | None) -> bool:
    """The record is the kind of result the declaration names, with no default filling a gap."""
    if declared is None or declared.format is None or result.get("format") != declared.format:
        return False
    if declared.origin is not None:
        return result.get("origin") == declared.origin and "profile" not in result
    return isinstance(result.get("profile"), str) and result["profile"] == declared.profile


def evaluation_presence(result: Mapping[str, Any], declared: CheckDeclaration | None) -> EvidencePresence:
    """Typed evidence facts for one record. Each is a question about a specific field, so an
    empty or partial record cannot pass by being non-empty."""
    executed = result.get("executedVerifierSet")
    identity = executed.get("identity") if isinstance(executed, Mapping) else None
    identifier = result.get("id")
    return EvidencePresence(
        record_identified=isinstance(identifier, str) and bool(identifier),
        verdict_recorded=isinstance(result.get("status"), str),
        binding_established=execution_binding(result) != "UNESTABLISHED",
        declaration_matches=_declaration_matches(result, declared),
        bundle_identified=declared is not None and (
            not declared.bundle_declared or (isinstance(identity, str) and bool(identity))),
    )


def refusal_reason(evaluation: Mapping[str, Any]) -> str:
    """Why the kernel did not admit a check, in the order an operator can act on."""
    presence = evaluation.get("evidencePresence") or {}
    if evaluation.get("executionStatus") != "COMPLETED":
        return f"execution did not complete ({evaluation.get('executionStatus')})"
    if evaluation.get("evaluationOutcome") != "PASS":
        return f"the completed evaluation did not pass ({evaluation.get('evaluationOutcome')})"
    if evaluation.get("bundleIntegrity") not in ("NOT_COVERED", "VERIFIED"):
        return f"verifier bundle integrity is {evaluation.get('bundleIntegrity')}"
    if evaluation.get("reportIntegrity") == "UNTRUSTED":
        return "report bytes were reachable by candidate code"
    missing = [name for name, value in presence.items() if value is not True]
    if missing:
        return "evidence incomplete: " + ", ".join(missing)
    return "not admitted"


def roster_decision(
    required: Sequence[str],
    results_by_id: Mapping[str, Any],
    declarations: Mapping[str, CheckDeclaration],
    *,
    empty_declared: bool,
    core: Core | None = None,
) -> dict[str, Any]:
    """The kernel's verdict on a roster: every required check recomputed from its raw record,
    admitted by Worldline.Evaluation.Admissible, and the list judged by Roster_Complete.

    Saved classifications are never read here. Python assembles the list in policy order; the
    per-check decision and the completeness rule (including the empty-roster case) are the
    kernel's.
    """
    core = core or Core.shared()
    admitted: list[bool] = []
    refused: list[dict[str, str]] = []
    evaluations: dict[str, dict[str, Any]] = {}
    for check_id in required:
        result = results_by_id.get(check_id)
        if not isinstance(result, Mapping):
            admitted.append(False)
            refused.append({"id": check_id, "reason": "no execution record"})
            continue
        evaluation = evaluation_record(result, declared=declarations.get(check_id), core=core)
        evaluations[check_id] = evaluation
        ok = evaluation["admissibleForPromotion"] is True
        admitted.append(ok)
        if not ok:
            refused.append({"id": check_id, "reason": refusal_reason(evaluation)})
    complete = core.evaluation_roster_complete(admitted, empty_declared=empty_declared)
    return {"complete": complete, "required": list(required), "emptyDeclared": empty_declared,
            "refused": refused, "evaluations": evaluations}


def evaluation_record(result: Mapping[str, Any], *, declared: CheckDeclaration | None,
                      core: Core | None = None) -> dict[str, Any]:
    """Three facts that were being carried as one, and could therefore contradict each other.

    `executionBinding` answered "was an intact bundle staged?" while being read as "did the
    authorised examiner run?". A preserved counterexample makes the gap concrete: a candidate
    that owned the harness produced `status: PASS` from fabricated output, the examiner never
    executed — and the binding still said BOUND, because the bundle had indeed been staged and
    its descriptors had indeed not moved. Both statements were true. Together they were a lie.

    bundleIntegrity     were the intended evaluator artifacts staged and protected under the
                        recorded identity?
    executionStatus     did the trusted evaluation reach the examiner and complete, or fail at
                        an identifiable stage?
    evaluationOutcome   did a completed evaluation accept or reject the candidate?

    Only `executionStatus == COMPLETED` may contribute to promotion admissibility. An intact
    bundle whose evaluation never reached it is NOT an ordinary pass and is not a failed check
    either: it is an evaluation that did not happen.
    """
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
    # Python only maps observations to finite categories. The SPARK core determines execution,
    # outcome and bundle integrity; malformed and unknown categories remain non-promotable.
    core = core or Core.shared()
    classification = core.evaluation_classify(facts)
    execution, outcome, integrity = (
        classification.execution, classification.outcome, classification.bundle)

    # Legacy reports come from the writable candidate overlay. Private reports additionally
    # need positive, invocation-bound observations of the separate examiner domain.
    report_format = result.get("format")
    report_based = report_format in ("junit", "gnatprove", "worldline-benchmark-v1")
    report_integrity = ("VERIFIED" if _private_report_verified(result, execution=execution, integrity=integrity)
                        else "UNTRUSTED") if report_based else "NOT_APPLICABLE"
    # Evidence presence is a set of typed facts about named fields, checked against the policy's
    # declaration for this check. The roster -- every required check, and what an empty one
    # means -- is decided separately by the kernel's Roster_Complete (see roster_decision).
    presence = evaluation_presence(result, declared)
    admissible = core.evaluation_admissible(
        classification, report_integrity=report_integrity, presence=presence)
    return {
        "bundleIntegrity": integrity,
        "executionStatus": execution,
        "evaluationOutcome": outcome,
        "reportIntegrity": report_integrity,
        "evidencePresence": {
            "recordIdentified": presence.record_identified,
            "verdictRecorded": presence.verdict_recorded,
            "bindingEstablished": presence.binding_established,
            "declarationMatches": presence.declaration_matches,
            "bundleIdentified": presence.bundle_identified,
        },
        "admissibleForPromotion": admissible,
        "nonClaims": [
            "SPARK classifies the finite observations and decides this check's promotion"
            " admissibility. It does not prove that Python supplied authentic observations"
            " or that the complete policy roster is present.",
            "executionStatus COMPLETED means the service manager observed the examiner's exit"
            " and the runner produced a definite verdict. It does not authenticate bytes that"
            " the examiner or candidate wrote inside the sandbox, nor establish that the"
            " examiner's judgment is independent of candidate code run in-process.",
            "Report integrity VERIFIED requires the private examiner boundary, clean supervised"
            " completion, a private collector digest, and matching invocation, candidate and"
            " verifier identities. It does not prove examiner logic correct or make arbitrary"
            " candidate imports safe. Legacy reportTrust labels confer no authorization."
            if report_based else
            "The supervisor-observed exit status supports only the exit-format verdict; it"
            " does not imply anything about report files or candidate code run in-process.",
            "bundleIntegrity establishes that the declared artifacts were staged and did not move."
            " It does not establish that they were read.",
            "EVALUATOR_INCOMPLETE is raised from a conservative, module-level import analysis of"
            " the staged verifiers, for a FAIL only: a PASS resolved its imports, and the analysis"
            " cannot tell a missing helper from the candidate's module under test. Its absence"
            " does not establish that the evaluator was complete: a dynamic or guarded import can"
            " still fail at run time, and such a run is reported as an ordinary FAIL.",
            "evidencePresence records typed facts about named fields compared with the policy's"
            " declaration for this check; it does not authenticate the values those fields"
            " hold.",
            "This classification is total: every unrecognised, contradictory or malformed"
            " combination falls to UNCLASSIFIED with outcome NONE, never to a completed"
            " evaluation. UNASSESSED -- a world that ended before its checks ran -- is"
            " NOT_ATTEMPTED, not a completed failure.",
            "origin: engine is honoured only for a result that also has no exit code, no"
            " resultChannel and no staged bundle -- the shape only the engine's own in-process"
            " checks have. A forged result carrying the string but reaching finalization through"
            " the check runner is UNCLASSIFIED.",
        ],
    }


def execution_binding(result: Mapping[str, Any]) -> str:
    """Whether this result can be attached to the verifier bundle WORLDLINE authorised.

    BOUND         the declared bundle was staged from the trusted snapshot, its identities held
                  across the evaluation, and the pathnames still resolved to those objects.
    UNESTABLISHED a bundle was staged but something moved: content changed, a pathname was
                  rebound, or the re-reading failed. This is not a failed check — it is a check
                  whose provenance nobody can state, which is worse.
    NOT_COVERED   this check declares no verifier bundle, so there is nothing to bind. It may
                  still pass; it is simply not execution-bound, and the evidence says so rather
                  than letting silence imply coverage.

    Three outcomes on purpose. "The examiner ran and rejected the candidate", "we could not
    establish that the trusted examiner ran", and "this check is outside execution-identity
    coverage" are different facts, and the last must never be advertised as bound merely because
    its neighbours are.
    """
    executed = result.get("executedVerifierSet")
    if executed is None:
        return "NOT_COVERED"
    if not isinstance(executed, Mapping):
        return "UNESTABLISHED"
    if executed.get("stable") is True and not executed.get("changedDuringExecution"):
        return "BOUND"
    return "UNESTABLISHED"


class Finalizer:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        sandbox: BubblewrapSandbox,
        *,
        core: Core | None = None,
        toolchains: Sequence[str] = (),
    ) -> None:
        self.paths = paths
        self.store = store
        self.sandbox = sandbox
        self.core = core or Core.shared()
        self.toolchains = tuple(toolchains)
        self.environment = EnvironmentCapture(self.core)
        self.git = GitAdapter(self.core)

    def capture_candidate(self, world_value: str, overlays: Sequence[OverlayRoot]) -> CandidateSnapshot:
        """Copy and identify the agent tree before any evaluator can write to its view."""
        world = self.store.world(world_value)
        if world.state is not WorldState.MUTABLE:
            raise WorldlineError("INVALID_TRANSITION", "candidate capture requires a MUTABLE world")
        return self._capture_candidate(world, overlays)

    def _capture_candidate(self, world: World, overlays: Sequence[OverlayRoot]) -> CandidateSnapshot:
        """Materialize for pre-check capture or the legacy finalization path."""
        registered = self.store.roots()
        roots_by_key = {root.root_key: root for root in overlays}
        if len(roots_by_key) != len(overlays) or set(roots_by_key) != {root["root_key"] for root in registered}:
            raise WorldlineError("ROOT_SET_MISMATCH", "overlay roots do not match registered roots")
        if not registered:
            raise WorldlineError("ROOT_SET_MISMATCH", "candidate capture requires registered roots")
        parent = secure_directory(self.paths.overlays / world.instance_id)
        runtime = Path(tempfile.mkdtemp(prefix="candidate-snapshot-", dir=parent))
        materialized = runtime / "materialized"
        materialized.mkdir(mode=0o700)
        arguments: list[str] = []
        for root in registered:
            overlay = roots_by_key[root["root_key"]]
            if os.fsencode(overlay.target) != bytes(root["path"]):
                raise WorldlineError("ROOT_SET_MISMATCH", "overlay target differs from its registered root")
            arguments.extend((str(overlay.target), f"/run/worldline-runtime/materialized/{root['root_key']}"))
        primary = next((root for root in registered if root["primary_root"]), registered[0])
        spec = SandboxSpec(
            instance_id=world.instance_id,
            argv=trusted_inline(_COPY_SCRIPT, *arguments),
            cwd=roots_by_key[primary["root_key"]].target,
            environment={"PATH": "/usr/bin"},
            roots=tuple(overlays),
            runtime=runtime,
        )
        process = self.sandbox.launch_world(spec)
        _stdout, stderr = process.process.communicate(timeout=300)
        if process.process.returncode != 0:
            raise WorldlineError("MATERIALIZATION_FAILED",
                                 stderr.decode("utf-8", "replace").strip()
                                 or f"materializer exited {process.process.returncode}")
        manifests = self._capture_candidate_manifests(materialized, registered)
        return CandidateSnapshot(world.instance_id, materialized, manifests,
                                 Manifest.root_set_hash(manifests.values(), self.core))

    def _capture_candidate_manifests(self, directory: Path,
                                    registered: Sequence[Mapping[str, Any]]) -> dict[str, CapturedManifest]:
        result: dict[str, CapturedManifest] = {}
        for root in registered:
            root_key = root["root_key"]
            source = directory / root_key
            result[root_key] = Manifest.capture(
                source, logical_root=bytes(root["path"]), root_key=root_key, kind=root["kind"],
                core=self.core, repository=self.git.capture(source) if root["kind"] == "repo" else None,
            )
        return result

    def candidate_overlays(self, snapshot: CandidateSnapshot) -> tuple[OverlayRoot, ...]:
        """Shared scratch for private checks; retained under the world's ordinary overlay tree."""
        roots = self.store.roots()
        self._verify_candidate_snapshot(snapshot, self.store.world(snapshot.world_instance), roots)
        result: list[OverlayRoot] = []
        for root in roots:
            key = root["root_key"]
            lower = snapshot.directory / key
            private = snapshot.directory.parent / "check-overlays" / key
            upper = secure_directory(private / "upper")
            work = secure_directory(private / "work")
            if any(upper.iterdir()) or any(work.iterdir()):
                raise WorldlineError("OVERLAY_NOT_EMPTY", "private check overlays must start empty")
            shutil.copystat(lower, upper, follow_symlinks=False)
            result.append(OverlayRoot(key, lower, upper, work, Path(os.fsdecode(bytes(root["path"])))))
        return tuple(result)

    def _verify_candidate_snapshot(self, snapshot: CandidateSnapshot, world: World,
                                   registered: Sequence[Mapping[str, Any]]) -> None:
        if (snapshot.world_instance != world.instance_id
                or set(snapshot.manifests) != {root["root_key"] for root in registered}
                or Manifest.root_set_hash(snapshot.manifests.values(), self.core) != snapshot.root_hash):
            raise WorldlineError("CANDIDATE_SNAPSHOT_MISMATCH", "candidate snapshot identity does not match this world")
        # verify_content intentionally ignores several metadata fields. Recapture the full
        # manifests here so changed permissions, xattrs, links and repository facts also refuse.
        observed = self._capture_candidate_manifests(snapshot.directory, registered)
        if any(observed[key].canonical != expected.canonical for key, expected in snapshot.manifests.items()):
            raise WorldlineError("CANDIDATE_SNAPSHOT_CHANGED", "the pre-check candidate snapshot changed")

    def _verify_base(self, manifest: CapturedManifest, source: Path, root_key: str) -> None:
        # The base checkpoint is shared by every sibling and read by several finalizations at
        # once; a transient read failure here used to surface as a bare CORE_IO and kill the
        # world. Retry briefly, then fail by name with the root that could not be verified.
        last: WorldlineError | None = None
        for attempt in range(3):
            try:
                Manifest.verify_content(manifest, source, self.core)
                return
            except WorldlineError as exc:
                last = exc
                if not exc.code.startswith("CORE_"):
                    break
                time.sleep(0.5 * (attempt + 1))
        assert last is not None
        raise WorldlineError(
            "BASE_CHECKPOINT_UNVERIFIED",
            f"the checkpoint this world was forked from could not be verified for root {root_key}: {last.message}",
            {"rootKey": root_key, "base": str(source), "cause": last.as_dict()},
        )

    def finalize(
        self,
        world_value: str,
        overlays: Sequence[OverlayRoot],
        *,
        check_results: Sequence[dict[str, Any]],
        protected: Sequence[str] = (),
        validation: Mapping[str, Any] | None = None,
        required_checks: Sequence[str],
        agent_manifest: dict[str, Any],
        candidate_snapshot: CandidateSnapshot | None = None,
    ) -> World:
        world = self.store.world(world_value)
        if world.state is not WorldState.MUTABLE:
            raise WorldlineError("INVALID_TRANSITION", f"finalization requires MUTABLE world, got {world.state.value}")
        private_snapshot = candidate_snapshot is not None
        if candidate_snapshot is None:
            # Legacy checks historically contribute generated outputs to the payload. Preserve
            # that behavior and its limited source-binding claim; private evaluators must name
            # a snapshot chosen before their execution.
            if any(item.get("profile") == "private-evaluator-v1" and item.get("status") != "UNASSESSED"
                   for item in check_results):
                raise WorldlineError("CANDIDATE_SNAPSHOT_MISSING", "evaluated results require a pre-check candidate snapshot")
        world.transition(WorldState.FINALIZING, self.core)
        self.store.save_world(world)

        try:
            if candidate_snapshot is None:
                candidate_snapshot = self._capture_candidate(world, overlays)
            registered = self.store.roots()
            self._verify_candidate_snapshot(candidate_snapshot, world, registered)
            binding = candidate_snapshot.binding()
            for item in check_results:
                if item.get("profile") == "private-evaluator-v1" and item.get("status") != "UNASSESSED":
                    if item.get("candidateSnapshot") != binding:
                        raise WorldlineError("CANDIDATE_SNAPSHOT_MISMATCH",
                                             "check result does not name the pre-check candidate snapshot")

            payload = Path(world.payload_path)
            if payload.exists():
                raise WorldlineError("PAYLOAD_EXISTS", f"candidate payload already exists: {payload}")
            payload.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            os.rename(candidate_snapshot.directory, payload)
            manifests_directory = payload / "manifests"
            manifests_directory.mkdir(mode=0o700)
            candidate_manifests: dict[str, CapturedManifest] = {}
            base_manifests: dict[str, CapturedManifest] = {}
            dependency_roots: list[tuple[str, Path]] = []
            for root in registered:
                root_key = root["root_key"]
                logical = bytes(root["path"])
                candidate_source = payload / root_key
                base_source = Path(world.base_payload_path) / root_key
                candidate_manifest = candidate_snapshot.manifests[root_key]
                base_manifest_path = Path(world.base_payload_path) / "manifests" / f"{root_key}.json"
                if base_manifest_path.is_file():
                    base_manifest = Manifest.load(base_manifest_path, self.core)
                    self._verify_base(base_manifest, base_source, root_key)
                else:
                    base_repository = self.git.capture(base_source) if root["kind"] == "repo" else None
                    base_manifest = Manifest.capture(
                        base_source,
                        logical_root=logical,
                        root_key=root_key,
                        kind=root["kind"],
                        core=self.core,
                        repository=base_repository,
                    )
                candidate_manifest.save(manifests_directory / f"{root_key}.json")
                candidate_manifests[root_key] = candidate_manifest
                base_manifests[root_key] = base_manifest
                dependency_roots.append((root_key, candidate_source))

            base_root = Manifest.root_set_hash(base_manifests.values(), self.core)
            if base_root != world.base_root:
                raise WorldlineError(
                    "BASE_ROOT_MISMATCH",
                    "candidate base checkpoint differs from its claimed base",
                    {"claimed": world.base_root, "actual": base_root},
                )
            delta = Delta.compute_all(base_manifests, candidate_manifests, self.core)
            check_results = list(check_results)
            required_checks = list(required_checks)
            if protected:
                # Engine-enforced: PRIME's policy names the paths and the engine's own delta says
                # whether the candidate changed them; neither is the candidate's to rewrite. The
                # synthetic check is part of the evidence manifest like any other check.
                touched = sorted({op["pathDisplay"] for op in delta.value["operations"] if protected_matches(tuple(protected), op["pathDisplay"])})
                check_results.append(
                    {
                        "id": "protected-paths",
                        "kind": "policy",
                        "required": True,
                        "format": "engine",
                        # Stated, not inferred from an absent exit code: the engine computed
                        # this verdict itself from facts it owns. See evaluation_record.
                        "origin": "engine",
                        "covers": list(protected),
                        "status": "FAIL" if touched else "PASS",
                        "touched": touched,
                        "reason": ("the candidate changed protected paths: " + ", ".join(touched)) if touched else "no protected path changed",
                    }
                )
                required_checks.append("protected-paths")
            # These belong to the RECORD, so they are attached before the evidence manifest is
            # built and hashed -- not afterwards.
            #
            # `evidence_manifest` shallow-copies each result, so anything attached after it was
            # built lived only on the runner's own list. Finalization read the originals and
            # correctly degraded the world, but the COMMIT-time gate reads
            # `subject.evidence["checks"]`, i.e. the copies, where `executionBinding` and
            # `evaluation` were simply absent. Both of its guards therefore compared against
            # nothing: `executionBinding == "UNESTABLISHED"` could never be true, and a missing
            # `executionStatus` reads as None, which is permitted. The second gate that feeds
            # the kernel's completeness input was passing by not asking -- the exact failure its
            # own docstring warns about.
            #
            # Each record is classified against the policy's declaration for its check, from the
            # requirement this evaluation was bound to. Without a requirement nothing is declared,
            # and a check with no declaration is never admitted.
            requirement = validation.get("requirement") if validation is not None else None
            declarations = check_declarations(requirement)
            # WORLDLINE's own results have fixed shapes that no policy writes: the agent's exit is
            # always on this roster, and protected-paths whenever this finalization protects
            # anything.
            declarations["agent"] = ENGINE_DECLARATIONS["agent"]
            if protected:
                declarations["protected-paths"] = ENGINE_DECLARATIONS["protected-paths"]
            for item in check_results:
                item["executionBinding"] = execution_binding(item)
                item["evaluation"] = evaluation_record(
                    item, declared=declarations.get(str(item.get("id"))), core=self.core)
            dependencies = capture_dependencies(dependency_roots, self.core)
            dependency_counts = [item["count"] for item in dependencies]
            dependency_count = (
                sum(dependency_counts)
                if all(isinstance(value, int) for value in dependency_counts)
                else None
            )
            context = None
            if validation is not None:
                # Verifier bytes as they were INSIDE the candidate's tree: a candidate that
                # rewrote its examiner is named here (and refused at prepare) even when the
                # path was not listed as protected.
                from .validation import build_context, resolve_verifiers
                project = validation["project"]
                sources = {root_key: payload / root_key for root_key in [r["root_key"] for r in validation["roots"]]}
                context = build_context(
                    requirement=validation["requirement"],
                    candidate={"instanceId": world.instance_id, "alias": world.alias, "baseRoot": world.base_root, "rootSetHash": world.root_set_hash, "missionHash": world.mission_hash},
                    prime_at_fork=validation["primeAtFork"],
                    roots=validation["roots"],
                    results=check_results,
                    candidate_verifiers=resolve_verifiers(project, validation["roots"], sources),
                    adapter=validation["adapter"],
                    evaluated_at=utc_now(),
                    core=self.core,
                )
            evidence = evidence_manifest(
                check_results,
                self.core,
                validation=context,
                metrics={
                    "dependencyCount": dependency_count,
                    "nonblankSourceLines": self._source_lines(candidate_manifests, payload),
                    "dependencyRecords": dependencies,
                    "generatedClassifiers": agent_manifest.get("generatedClassifiers", []),
                    "candidateSnapshot": binding if private_snapshot else None,
                    "evaluationWorkspace": {
                        "writes": ("private evaluator writes are discarded; the pre-check snapshot becomes the payload"
                                   if private_snapshot else "legacy check outputs are included in the payload"),
                        "nonClaims": ([
                            "The snapshot identifies the initial input of mutable check overlays."
                            " It does not establish that an examiner saw unchanged bytes throughout"
                            " execution; transient or persistent writes in its scratch view can"
                            " affect its judgment. Private check-produced artifacts are not promoted.",
                        ] if private_snapshot else [
                            "Legacy checks run in the same writable overlay that is materialized"
                            " afterward. Their evidence does not establish that the final payload"
                            " remained unchanged throughout evaluation.",
                        ]),
                    },
                },
            )
            try:
                containers = DockerAdapter(self.core).capture(
                    world.instance_id,
                    world_roots={
                        root_key: source
                        for root_key, source in dependency_roots
                    },
                )
            except WorldlineError as exc:
                containers = [
                    {
                        "state": "UNAVAILABLE",
                        "reason": exc.message,
                    }
                ]
            environment = self.environment.capture(
                processes=[
                    OwnedProcess(
                        pid=agent_manifest.get("mainPid") if isinstance(agent_manifest.get("mainPid"), int) else None,
                        world_instance=world.instance_id,
                        systemd_unit=agent_manifest.get("systemdUnit"),
                        role="agent",
                        argv=tuple(agent_manifest.get("argv", [])),
                        cwd=os.fsencode(agent_manifest.get("cwd", "")),
                    )
                ],
                toolchains=self.toolchains,
                dependency_roots=dependency_roots,
                agent=agent_manifest,
                evidence=evidence,
                workspace=world.workspace,
                containers=containers,
            )
            environment.save(manifests_directory / "environment.json")
            atomic_write_json(manifests_directory / "evidence.json", evidence)
            atomic_write_json(manifests_directory / "agent.json", agent_manifest)
            world.components = {
                **Manifest.component_roots(candidate_manifests.values(), self.core),
                "environment": environment.root_hash,
                "evidence": evidence["root"],
            }
            ghost_objective = world.evidence.get("ghostObjective")
            if isinstance(ghost_objective, str):
                evidence["ghostObjective"] = ghost_objective
            world.evidence = evidence
            world.agent_reference = agent_manifest.get("sessionReference")
            world.delta_hash = delta.delta_hash
            world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
            world.establish_identity(self.core)
            results_by_id = {item.get("id"): item for item in check_results}
            # The kernel decides the roster: each required record is recomputed from its raw
            # fields (never the saved classification), admitted by Evaluation.Admissible, and the
            # list judged by Roster_Complete. The runner always puts the agent's own exit on it;
            # an empty roster counts only when the requirement's policy declared one.
            roster = roster_decision(list(required_checks), results_by_id, declarations,
                                     empty_declared=required_roster(requirement)[1], core=self.core)
            world.risk = "HIGH" if not roster["complete"] else "MEDIUM"
            world.transition(WorldState.VALID if roster["complete"] else WorldState.DEGRADED, self.core)
            self.store.save_world(world)
            self._make_readonly(payload)
            return world
        except BaseException as exc:
            if world.state is WorldState.FINALIZING:
                error = exc.as_dict() if isinstance(exc, WorldlineError) else {
                    "code": "FINALIZATION_FAILED",
                    "message": f"{type(exc).__name__}: {exc}",
                    "details": {},
                }
                world.evidence = {
                    "summary": "FAIL",
                    "checks": list(check_results),
                    "materializationError": {"type": type(exc).__name__, "message": str(exc)},
                    # One place every surface reads the reason a world is DEAD from.
                    "supervision": error,
                }
                world.transition(WorldState.DEAD, self.core)
                self.store.save_world(world)
            raise

    @staticmethod
    def _source_lines(manifests: Mapping[str, CapturedManifest], payload: Path) -> int:
        extensions = {
            b".adb", b".ads", b".c", b".cc", b".cpp", b".go", b".h", b".hpp",
            b".java", b".js", b".jsx", b".kt", b".py", b".rb", b".rs", b".ts",
            b".tsx",
        }
        count = 0
        for root_key, manifest in manifests.items():
            for relative, entry in manifest.entry_map().items():
                if entry["type"] != "file" or os.path.splitext(relative)[1].lower() not in extensions:
                    continue
                try:
                    text = (payload / root_key / os.fsdecode(relative)).read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                count += sum(bool(line.strip()) for line in text.splitlines())
        return count

    @staticmethod
    def _make_readonly(payload: Path) -> None:
        for current, directories, files in os.walk(payload, topdown=False, followlinks=False):
            current_path = Path(current)
            for name in files:
                path = current_path / name
                if path.is_symlink():
                    continue
                os.chmod(path, stat.S_IMODE(path.stat().st_mode) & ~0o222)
            for name in directories:
                path = current_path / name
                if path.is_symlink():
                    continue
                os.chmod(path, stat.S_IMODE(path.stat().st_mode) & ~0o222)
        os.chmod(payload, stat.S_IMODE(payload.stat().st_mode) & ~0o222)

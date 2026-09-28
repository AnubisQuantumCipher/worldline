"""Private report promotion requires complete, mutually bound supervisor facts."""
from __future__ import annotations

import base64
import copy
import hashlib
import unittest

from worldline.finalize import evaluation_record


def observation(role: str) -> dict:
    examiner = role == "examiner"
    uid = {"examiner": 0, "worker": 1, "candidate": 2}[role]
    return {
        "role": role, "uid": uid, "gid": uid,
        "status": {"Uid": " ".join([str(uid)] * 4), "Gid": " ".join([str(uid)] * 4),
                   "Groups": "", "NoNewPrivs": "1", "CapEff": "0000000000000000",
                   "CapPrm": "0000000000000000", "CapBnd": "0000000000000000", "CapAmb": "0000000000000000"},
        "namespaces": {"user": "user:[100]", "pid": "pid:[101]" if examiner else "pid:[102]",
                       "mnt": "mnt:[103]" if examiner else "mnt:[104]"},
        "reportMounted": examiner, "brokerMounted": examiner,
        "workerBrokerMounted": role == "worker",
    }


def private_result() -> dict:
    payload = b"private report bytes"
    return {
        "id": "exam", "profile": "private-evaluator-v1", "format": "junit",
        "status": "PASS", "origin": "supervisor", "exitCode": 0,
        "resultChannel": {"accepted": True, "recordProducer": "daemon-outside-sandbox"},
        "supervision": {"kind": "SUPERVISED", "started": True, "result": "success",
                        "stoppedByManager": False, "launcherExit": 0, "exitCode": None, "exitStatus": None},
        "executedVerifierSet": {"identity": "verifier-id", "stable": True, "changedDuringExecution": []},
        "candidateSnapshot": {"rootSetHash": "candidate-id"},
        "privateReport": {"collection": "private-directory", "runId": "run-id", "checkId": "exam",
                          "candidateIdentity": "candidate-id", "verifierIdentity": "verifier-id",
                          "sha256": hashlib.sha256(payload).hexdigest(), "sizeBytes": len(payload),
                          "payloadB64": base64.b64encode(payload).decode("ascii")},
        "evaluatorBoundary": {"profileId": "private-evaluator-v1", "runId": "run-id",
                              "examinerReturnCode": 0, "bootstrapExitCode": 0,
                              "managerBootstrapProperties": {"NoNewPrivileges": "no"},
                              "rolesCompleted": True, "reportMountExclusive": True,
                              "examiner": observation("examiner"),
                              "workers": [{"returncode": 0, "observation": observation("worker")}]},
    }


class PrivateReportAdmission(unittest.TestCase):
    def assert_refused(self, result: dict) -> None:
        value = evaluation_record(result)
        self.assertEqual(value["reportIntegrity"], "UNTRUSTED")
        self.assertFalse(value["admissibleForPromotion"])

    def test_complete_private_reports_are_admitted_for_existing_formats(self) -> None:
        for report_format in ("junit", "gnatprove", "worldline-benchmark-v1"):
            with self.subTest(format=report_format):
                result = private_result()
                result["format"] = report_format
                self.assertEqual(evaluation_record(result)["reportIntegrity"], "VERIFIED")
                self.assertTrue(evaluation_record(result)["admissibleForPromotion"])

    def test_examiner_only_analysis_does_not_require_a_candidate_subprocess(self) -> None:
        result = private_result()
        result["evaluatorBoundary"]["workers"] = []
        self.assertTrue(evaluation_record(result)["admissibleForPromotion"])

    def test_expected_worker_failure_can_be_judged_by_the_trusted_examiner(self) -> None:
        result = private_result()
        result["evaluatorBoundary"]["workers"][0]["returncode"] = 1
        self.assertTrue(evaluation_record(result)["admissibleForPromotion"])

    def test_private_report_failure_is_authentic_but_not_admissible(self) -> None:
        result = private_result()
        result["status"] = "FAIL"
        result["exitCode"] = 1
        result["supervision"].update({"result": "failure", "launcherExit": 1, "exitStatus": 1})
        result["evaluatorBoundary"].update({"examinerReturnCode": 1, "bootstrapExitCode": 1})
        value = evaluation_record(result)
        self.assertEqual(value["reportIntegrity"], "VERIFIED")
        self.assertFalse(value["admissibleForPromotion"])

    def test_legacy_profile_cannot_borrow_private_boundary_labels(self) -> None:
        result = private_result()
        result["profile"] = "legacy"
        self.assert_refused(result)

    def test_missing_or_malformed_fact_blocks_admission(self) -> None:
        for key in ("resultChannel", "supervision", "evaluatorBoundary", "privateReport",
                    "candidateSnapshot", "executedVerifierSet"):
            for malformed in (None, [], "unverified", True):
                with self.subTest(key=key, malformed=malformed):
                    result = private_result()
                    result[key] = malformed
                    self.assert_refused(result)
        for key in ("examiner", "workers", "rolesCompleted", "reportMountExclusive", "runId", "profileId"):
            with self.subTest(missing_boundary=key):
                result = private_result()
                del result["evaluatorBoundary"][key]
                self.assert_refused(result)

    def test_invocation_identities_and_digest_must_match(self) -> None:
        for key in ("runId", "checkId", "candidateIdentity", "verifierIdentity", "sha256", "collection"):
            with self.subTest(key=key):
                result = private_result()
                result["privateReport"][key] = "different"
                self.assert_refused(result)
        result = private_result()
        result["privateReport"]["sizeBytes"] = True
        self.assert_refused(result)

    def test_retained_payload_must_match_the_collector_digest_and_size(self) -> None:
        for payload in (None, "not base64", base64.b64encode(b"different bytes").decode("ascii")):
            with self.subTest(payload=payload):
                result = private_result()
                result["privateReport"]["payloadB64"] = payload
                self.assert_refused(result)
        result = private_result()
        result["privateReport"]["sha256"] = hashlib.sha256(b"different bytes").hexdigest()
        self.assert_refused(result)
        result = private_result()
        result["privateReport"]["sizeBytes"] = 1
        self.assert_refused(result)

    def test_missing_verifier_coverage_cannot_admit_a_private_report(self) -> None:
        result = private_result()
        result["executedVerifierSet"] = {}
        self.assert_refused(result)

    def test_boundary_or_supervisor_failure_blocks_admission(self) -> None:
        changes = (
            ("supervision", "kind", "INDETERMINATE"), ("supervision", "started", False),
            ("supervision", "result", "failure"), ("supervision", "stoppedByManager", True),
            ("supervision", "launcherExit", 1), ("supervision", "exitStatus", False),
            ("resultChannel", "accepted", False), ("resultChannel", "recordProducer", "examiner"),
            ("evaluatorBoundary", "error", "incomplete"),
            ("evaluatorBoundary", "reportMountExclusive", False),
            ("executedVerifierSet", "stable", False),
        )
        for section, key, value in changes:
            with self.subTest(section=section, key=key):
                result = private_result()
                result[section][key] = value
                self.assert_refused(result)
        result = private_result()
        result["exitCode"] = False
        self.assert_refused(result)

    def test_candidate_principal_is_admitted_only_under_its_own_label(self) -> None:
        def with_entry(principal: str | None, role: str) -> dict:
            result = private_result()
            entry = {"returncode": 0, "observation": observation(role)}
            if principal is not None:
                entry["principal"] = principal
            result["evaluatorBoundary"]["workers"].append(entry)
            return result

        self.assertTrue(evaluation_record(with_entry("candidate", "candidate"))["admissibleForPromotion"])
        # A candidate relabelled, or left unlabelled and so defaulted, as a worker fails the
        # worker pins; a worker relabelled as a candidate fails the candidate pins.
        for principal, role in (("worker", "candidate"), (None, "candidate"), ("candidate", "worker"),
                                ("examiner", "candidate"), ("root", "candidate")):
            with self.subTest(principal=principal, role=role):
                self.assert_refused(with_entry(principal, role))
        shared = with_entry("candidate", "candidate")
        shared["evaluatorBoundary"]["workers"][1]["observation"].update({"uid": 1, "gid": 1})
        self.assert_refused(shared)
        # The worker-broker mount is pinned per role on its own, independent of the UID pin.
        for role, mounted in (("worker", False), ("candidate", True)):
            with self.subTest(role=role, workerBrokerMounted=mounted):
                result = with_entry(role, role)
                result["evaluatorBoundary"]["workers"][1]["observation"]["workerBrokerMounted"] = mounted
                self.assert_refused(result)

    def test_role_identity_namespaces_privileges_and_mounts_are_required(self) -> None:
        baseline = private_result()
        changes = (
            (("uid",), 0), (("gid",), True), (("reportMounted",), True), (("brokerMounted",), True),
            (("status", "NoNewPrivs"), "0"), (("status", "CapEff"), "0001"),
            (("status", "CapBnd"), ""), (("status", "Groups"), "0"),
            (("status", "Uid"), "0 0 0 0"), (("namespaces", "pid"), "pid:[101]"),
            (("namespaces", "mnt"), "mnt:[103]"), (("namespaces", "user"), "user:[200]"),
        )
        for path, value in changes:
            with self.subTest(path=path):
                result = copy.deepcopy(baseline)
                target = result["evaluatorBoundary"]["workers"][0]["observation"]
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                self.assert_refused(result)


if __name__ == "__main__":
    unittest.main()

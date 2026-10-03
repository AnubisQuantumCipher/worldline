"""Named D26 observation producer. This is not an admission predicate.

Unknown facts remain false. The SPARK wire owns the conjunction, classification,
report-integrity and promotion rules. Parser/producer/provenance proof remains open.
"""
from collections.abc import Mapping
import base64, binascii, hashlib, json, re
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET
from .report import MAX_REPORT_BYTES

FACT_NAMES = ('Private_Profile', 'Exit_Integer_Nonnegative', 'Records_Present',
 'Channel_Daemon_Accepted', 'Supervision_Clean', 'Boundary_Consistent',
 'Report_Mount_Exclusive', 'Collected_Privately', 'Identities_Match',
 'Digest_Matches', 'Examiner_Observed', 'Workers_Separated',
 'Status_Rederived', 'Examiner_Audit_Clean')

def report_status(result, payload):
    """Rederive with the SAME current parser and its original accepted cases.

    This reuse is not a parser proof. The full strict-parser obligation stays
    open; this producer must not silently strengthen a numeric/report policy.
    """
    if type(result.get('exitCode')) is not int or payload is None:
        return None
    if result.get('format') not in ('junit', 'gnatprove', 'worldline-benchmark-v1'):
        return None
    from types import SimpleNamespace
    from .checks import CheckRunner
    check = SimpleNamespace(format=result['format'], profile=result.get('profile'))
    return CheckRunner._parse(None, check, result['exitCode'], payload, b'', payload)['status']


def report_payload(result):
    report = result.get('privateReport')
    if not isinstance(report, Mapping): return None
    encoded = report.get('payloadB64')
    if not isinstance(encoded, str) or len(encoded) > ((MAX_REPORT_BYTES + 2) // 3) * 4: return None
    try: payload = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error): return None
    if len(payload) > MAX_REPORT_BYTES: return None
    return payload

def report_facts(result):
    from .finalize import _private_role_observed
    f = dict.fromkeys(FACT_NAMES, False)
    f['Private_Profile'] = result.get('profile') == 'private-evaluator-v1' and result.get('origin') == 'supervisor'
    code = result.get('exitCode')
    f['Exit_Integer_Nonnegative'] = type(code) is int and code >= 0
    values = [result.get(x) for x in ('resultChannel','supervision','evaluatorBoundary','privateReport','candidateSnapshot','executedVerifierSet')]
    f['Records_Present'] = all(isinstance(x, Mapping) for x in values)
    if not f['Records_Present']: return tuple(f[x] for x in FACT_NAMES)
    channel, supervision, boundary, report, snapshot, executed = values
    f['Channel_Daemon_Accepted'] = channel.get('accepted') is True and channel.get('recordProducer') == 'daemon-outside-sandbox'
    f['Supervision_Clean'] = (f['Exit_Integer_Nonnegative'] and supervision.get('kind') == 'SUPERVISED'
        and supervision.get('started') is True and supervision.get('stoppedByManager') is False
        and supervision.get('result') == ('success' if code == 0 else 'failure')
        and type(supervision.get('launcherExit')) is int and supervision['launcherExit'] == code
        and supervision.get('exitCode') in (None, 'exited')
        and (supervision.get('exitStatus') is None or (type(supervision['exitStatus']) is int and supervision['exitStatus'] == code)))
    f['Boundary_Consistent'] = (boundary.get('profileId') == result.get('profile')
        and boundary.get('error') is None and type(boundary.get('examinerReturnCode')) is int
        and boundary['examinerReturnCode'] == code and type(boundary.get('bootstrapExitCode')) is int
        and boundary['bootstrapExitCode'] == code and isinstance(boundary.get('managerBootstrapProperties'), Mapping)
        and boundary['managerBootstrapProperties'].get('NoNewPrivileges') == 'no' and boundary.get('rolesCompleted') is True)
    f['Report_Mount_Exclusive'] = boundary.get('reportMountExclusive') is True
    f['Collected_Privately'] = report.get('collection') == 'private-directory'
    pairs = (('runId', boundary.get('runId')), ('checkId', result.get('id')),
             ('candidateIdentity', snapshot.get('rootSetHash')), ('verifierIdentity', executed.get('identity')))
    f['Identities_Match'] = all(isinstance(expected, str) and bool(expected) and '\x00' not in expected
                              and report.get(key) == expected for key, expected in pairs)
    payload = report_payload(result); digest = report.get('sha256'); size = report.get('sizeBytes')
    f['Digest_Matches'] = (payload is not None and isinstance(digest, str)
        and re.fullmatch(r'[0-9a-f]{64}', digest) is not None and type(size) is int
        and 0 < size <= MAX_REPORT_BYTES and len(payload) == size and hashlib.sha256(payload).hexdigest() == digest)
    examiner, workers = boundary.get('examiner'), boundary.get('workers')
    f['Examiner_Observed'] = _private_role_observed(examiner, 'examiner')
    separated = f['Examiner_Observed'] and isinstance(workers, list)
    groups = {'worker': [], 'candidate': []}
    if separated:
        for worker in workers:
            if not isinstance(worker, Mapping) or type(worker.get('returncode')) is not int: separated = False; break
            observation, role = worker.get('observation'), worker.get('principal', 'worker')
            if role not in groups or not _private_role_observed(observation, role): separated = False; break
            if (observation['namespaces']['user'] != examiner['namespaces']['user']
                or any(observation['namespaces'][k] == examiner['namespaces'][k] for k in ('pid','mnt'))
                or observation.get('uidMap') != examiner.get('uidMap') or observation.get('gidMap') != examiner.get('gidMap')):
                separated = False; break
            groups[role].append(observation)
        if separated:
            separated = all(c['uid'] != w['uid'] and c['gid'] != w['gid'] for c in groups['candidate'] for w in groups['worker'])
    f['Workers_Separated'] = separated
    derived = report_status(result, payload)
    f['Status_Rederived'] = derived is not None and result.get('status') == derived
    # Recompute the static observation over retained staged bytes. This is
    # separate from complete confinement/custody and cannot establish it.
    from .examiner_audit import report_audit_clean
    f['Examiner_Audit_Clean'] = report_audit_clean(result)
    return tuple(f[x] for x in FACT_NAMES)

"""Raw report acquisition helpers and rendering of native-derived report facts."""
from collections.abc import Mapping
import base64
import binascii
from .report import MAX_REPORT_BYTES

FACT_NAMES = ('Private_Profile', 'Exit_Integer_Nonnegative', 'Records_Present',
 'Channel_Daemon_Accepted', 'Supervision_Clean', 'Boundary_Consistent',
 'Report_Mount_Exclusive', 'Collected_Privately', 'Identities_Match',
 'Digest_Matches', 'Examiner_Observed', 'Workers_Separated',
 'Status_Rederived', 'Examiner_Audit_Clean')


def report_payload(result):
    """Decode the original captured report envelope, not its authority."""
    report = result.get('privateReport')
    if not isinstance(report, Mapping):
        return None
    encoded = report.get('payloadB64')
    if not isinstance(encoded, str) or len(encoded) > ((MAX_REPORT_BYTES + 2) // 3) * 4:
        return None
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        return None
    if len(payload) > MAX_REPORT_BYTES:
        return None
    return payload


def report_status(result, payload, *, core=None):
    from types import SimpleNamespace
    from .core import Core
    from .report_parser import parse
    if type(result.get('exitCode')) is not int:
        return None
    check = SimpleNamespace(format=result.get('format'), profile=result.get('profile'))
    parsed = parse(Core.shared() if core is None else core, check, result['exitCode'],
                   b'' if payload is None else payload, b'', payload)
    return parsed['status']


def report_facts(result, *, core=None):
    """Diagnostic projection only; the producer and authority consume raw bytes."""
    from .evaluation_wire import record
    return tuple(bool(value) for value in record(result, None, core=core).native().report_facts)

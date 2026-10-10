"""Assertions over genuine recorded original inputs, never synthetic fixtures.

Tags are earned by an actual native observation and its original lossless input.
A requested but unobserved domain fails rather than being labeled by case name.
"""
from pathlib import Path

SUBJECT_CASES = frozenset(('REQUEST_QUEUED', 'REQUEST_TRANSFER_INTENT', 'REQUEST_INTAKE',
    'REQUEST_ABANDON', 'REQUEST_RESPONDED', 'REQUEST_LOST', 'DRAIN_STOP_INTENT',
    'DRAIN_FREEZE', 'DRAIN_OFD_EVIDENCE', 'DRAIN_INTAKE', 'DRAIN_ABANDON',
    'DRAIN_RELEASED', 'DRAIN_RECLAIMED'))
QUANTITIES = frozenset(('capacity', 'amount', 'observed_usage', 'held_total', 'charged_total',
    'policy_epoch', 'resource_epoch', 'expected_epoch', 'next_subgeneration', 'reattach_epoch'))


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def wide_original(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in QUANTITIES:
                if type(item) is int and (item < -(1 << 63) or item > (1 << 64) - 1):
                    return True
                if type(item) is bytes and len(item) > 8:
                    return True
            if wide_original(item):
                return True
    elif isinstance(value, (list, tuple)):
        return any(wide_original(item) for item in value)
    return False


def carried(value):
    if isinstance(value, dict):
        if value.get('mode') in ('RELAY', 'CARRY'):
            return True
        return any(carried(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(carried(item) for item in value)
    return False


def assert_recorders(recorders, required_kinds, required_controls, required_subject_cases):
    from custody_runtime_controls_v35 import KINDS, CONTROLS, sha
    from worldline.root_worker_codec import scoped_restore_archive, raw_restore_archive, raw_archive
    require(set(required_kinds) <= KINDS and set(required_controls) <= CONTROLS
            and set(required_subject_cases) <= SUBJECT_CASES, 'CONTROL_ORIGINAL_DOMAIN_CHANGED')
    positives = set()
    subjects = set()
    evidence = []
    for recorder in recorders:
        original_pending = recorder.pending
        try:
            for row in recorder.rows:
                raw = (recorder.directory / row['input']['path']).read_bytes()
                require(sha(raw) == row['input']['sha256'], 'CONTROL_ORIGINAL_INPUT_CHANGED')
                value = scoped_restore_archive(raw)
                candidate = value['candidate']
                require(value['schema'] == 'worldline.custody-mutation-v2'
                        and candidate['kind'] == row['kind'] and candidate['operation'] == row['operation'],
                        'CONTROL_ACTUAL_CANDIDATE_RECORD_SPLIT')
                wrapper = candidate['record']
                original = raw_restore_archive(wrapper['original'])
                require(raw_archive(original) == wrapper['original'], 'CONTROL_ORIGINAL_LOSSLESS_BYTES_CHANGED')
                recorder.pending = row
                ready = row['expected_status'] == 0 and 'delta' in row and 'context' in row
                if ready:
                    positives.add(row['kind'])
                    subject_kind = candidate['subject_kind']
                    if row['kind'].startswith('REQUEST_'):
                        require(subject_kind == 'REQUEST', 'CONTROL_REQUEST_ORIGINAL_SUBJECT_CHANGED')
                        subjects.add(row['kind'])
                    elif row['kind'].startswith('DRAIN_'):
                        require(subject_kind == 'DESCRIPTOR', 'CONTROL_DESCRIPTOR_ORIGINAL_SUBJECT_CHANGED')
                        subjects.add(row['kind'])
                    if wide_original(original) or wide_original(wrapper['x5']['primitive_inputs']):
                        recorder.label('full-values')
                    roots = value['before']['roots']
                    if any(len(root) == 16 and root[2] != 'UNKNOWN' and root[3] is None
                           and root[5] is None and root[13] is None for root in roots):
                        recorder.label('nullable-inactive')
                    if row['kind'] in ('REQUEST_TRANSFER_INTENT', 'REQUEST_INTAKE'):
                        starter = wrapper['x5']['subject_evidence']['binding']['root_head']
                        root_ops = {event[4] for event in value['before']['events'] if event[1] == starter}
                        require(len(root_ops) == 1, 'CONTROL_ACTUAL_ORIGINAL_STARTER_ROOT_REQUIRED')
                        if candidate['operation'] not in root_ops:
                            recorder.label('independent-request-operation')
                    if row['kind'] in ('REQUEST_INTAKE', 'DRAIN_INTAKE') and carried(wrapper['x5']['subject_evidence']):
                        recorder.label('carry')
                    if row['kind'] in ('REQUEST_LOST', 'DRAIN_RECLAIMED', 'HISTORICAL_SETTLEMENT'):
                        require(candidate['actor'] in ('COLLECTOR', 'RECONCILER'),
                                'CONTROL_ORIGINAL_HISTORICAL_COLLECTOR_REQUIRED')
                        recorder.label('historical-cleanup')
                if 'uncertainty' in row:
                    capsule_raw = (recorder.directory / row['uncertainty']['path']).read_bytes()
                    require(sha(capsule_raw) == row['uncertainty']['sha256'],
                            'CONTROL_ACTUAL_UNCERTAINTY_CAPSULE_CHANGED')
                    uncertain = raw_restore_archive(capsule_raw)
                    require(uncertain['input'] == raw and uncertain['candidate'] == candidate['record']
                            and row.get('actual_error') is not None
                            and row['expected_status'] == uncertain['native_status']
                            and row['expected_position'] == uncertain['native_position']
                            and type(uncertain['applied_rows']) is bytes
                            and type(uncertain['attempted_event']) is dict,
                            'CONTROL_ACTUAL_POSTCOMMIT_UNCERTAINTY_REQUIRED')
                    recorder.label('uncertain')
                evidence.append({'original_input_sha256': sha(raw), 'kind': row['kind'],
                                 'native_status': row['expected_status'], 'controls': list(row['controls'])})
        finally:
            recorder.pending = original_pending
    tags = {tag for recorder in recorders for row in recorder.rows for tag in row['controls']}
    require(set(required_kinds) <= positives, 'CONTROL_REQUIRED_GENUINE_EVENT_CLASS_MISSING')
    require(set(required_controls) <= tags, 'CONTROL_REQUIRED_ACTUAL_EDGE_CASE_MISSING')
    require(set(required_subject_cases) <= subjects, 'CONTROL_FULL_ORIGINAL_SUBJECT_CASE_MISSING')
    return {'actual_positive_kinds': sorted(positives), 'actual_subject_cases': sorted(subjects),
            'actual_controls': sorted(tags), 'observed_original_assertions': evidence}

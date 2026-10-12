"""Committed original-domain case IDs and actual action recipes.

The selected owner input binds genuine original configurations, requests,
actors, assertions and timeouts; it cannot replace these recipes or narrow the
native roster. Paths refer to future explicitly constructed disposable outputs,
not to claimed available fixtures. Only actual captured decisions earn credit.
"""
from __future__ import annotations

ROOT_SUCCESS = ('PREPARED', 'HELD', 'RUNNING', 'EXECUTION_NATIVE', 'EXECUTION_ACK',
    'HANDOFF_INTENT', 'FRONT_CLOSE_INTENT', 'FRONT_CLOSED', 'TRANSFER_SENT',
    'ROSTER_EVIDENCE', 'CUSTODY_ACK', 'ORIGINAL_PROGRESS', 'ORIGINAL_RESULT',
    'HANDLER_TERMINAL', 'WORKER_RELINQUISH', 'CUSTODY_RETURNED', 'CLOSED_NS',
    'CLOSED_OUTER', 'CLOSED_RAW', 'CLOSED_WITNESS', 'PHYSICAL_SETTLED',
    'HISTORICAL_SETTLEMENT', 'FRONT_RECONSTRUCTION', 'FRONT_OWNED')

CASE_IDS = ('original-root-success', 'original-request-independent', 'original-request-abandon',
    'original-request-lost-worker', 'original-drain-relay', 'original-drain-abandon',
    'original-drain-reclaimed-worker', 'original-root-unlaunched-refusal',
    'original-root-handoff-abort', 'original-root-crash-entry', 'original-root-crash-exit-lost-ack',
    'original-root-readback-uncertain', 'original-root-exact-retry', 'original-root-stale-cas',
    'original-root-full-values', 'original-multiroot-carrier-relay',
    'original-historical-nullable', 'retained-original-startup-resource-assertions')

CASE_IDS = CASE_IDS + ('original-root-transfer-abandon',)
DUPLEX_CASES = {
    'original-relay-gap-write': 'gap-write',
    'original-relay-shutdown-held': 'shutdown-held',
    'original-relay-eof-held': 'eof-held',
}
CASE_IDS = CASE_IDS + tuple(DUPLEX_CASES)

READER_CASES = ('original-drain-relay', 'original-drain-abandon',
    'original-drain-reclaimed-worker', 'original-multiroot-carrier-relay')


def client(inputs, name, wait):
    record = inputs['clients'][name]
    return {'kind': 'client', 'request': record['request'], 'early_envelope': record['early_envelope'],
        'environment': record['environment'], 'timeout': record['timeout'], 'wait': wait}


def fault(inputs, name, effect):
    record = inputs['faults'][name]
    return dict(record, kind='fault', target=name, effect=effect, wait=record['wait'])


def recipe(case, inputs):
    if case not in CASE_IDS:
        raise RuntimeError('ORIGINAL_CORPUS_UNKNOWN_COMMITTED_CASE')
    timeout = inputs['timeout']
    start = lambda: client(inputs, 'starter', False)
    wait = {'kind': 'wait-root-closure', 'timeout': timeout}
    clients = {'kind': 'wait-clients'}
    actions = []
    required_kinds = []; controls = []; subjects = []
    if case in ('original-root-success', 'original-root-full-values', 'original-historical-nullable'):
        actions = [start(), clients, wait]
        required_kinds = list(ROOT_SUCCESS)
        controls = (['full-values'] if case == 'original-root-full-values' else
                    ['historical-cleanup', 'nullable-inactive'] if case == 'original-historical-nullable' else [])
    elif case == 'original-request-independent':
        actions = [start(), {'kind': 'wait-custody-ack', 'timeout': timeout},
            client(inputs, 'independent', True), clients, wait]
        subjects = ['REQUEST_QUEUED', 'REQUEST_TRANSFER_INTENT', 'REQUEST_INTAKE', 'REQUEST_RESPONDED']
        required_kinds = subjects; controls = ['independent-request-operation']
    elif case == 'original-request-abandon':
        actions = [start(), {'kind': 'wait-custody-ack', 'timeout': timeout},
            client(inputs, 'independent', False),
            {'kind': 'abandon-request', 'timeout': timeout, 'request_id': inputs['request_id']}, clients, wait]
        subjects = ['REQUEST_ABANDON']; required_kinds = subjects
    elif case == 'original-request-lost-worker':
        actions = [start(), {'kind': 'wait-custody-ack', 'timeout': timeout},
            client(inputs, 'independent', False), fault(inputs, 'worker', 'kill-entry'), clients, wait]
        subjects = ['REQUEST_LOST']; required_kinds = subjects; controls = ['historical-cleanup']
    elif case in ('original-drain-relay', 'original-drain-abandon', 'original-drain-reclaimed-worker'):
        actions = [start(), {'kind': 'wait-custody-ack', 'timeout': timeout}]
        if case == 'original-drain-abandon':
            actions.append({'kind': 'abandon-reader', 'timeout': timeout, 'role': inputs['reader_role']})
            subjects = ['DRAIN_ABANDON']
        elif case == 'original-drain-reclaimed-worker':
            actions.append({'kind': 'transfer-readers', 'timeout': timeout})
            actions.append(fault(inputs, 'worker', 'kill-exit'))
            subjects = ['DRAIN_RECLAIMED']; controls = ['historical-cleanup']
        else:
            actions.append({'kind': 'transfer-readers', 'timeout': timeout})
            subjects = ['DRAIN_STOP_INTENT', 'DRAIN_FREEZE', 'DRAIN_OFD_EVIDENCE', 'DRAIN_INTAKE', 'DRAIN_RELEASED']
        actions.extend((clients, wait)); required_kinds = subjects
    elif case in ('original-root-unlaunched-refusal', 'original-root-handoff-abort'):
        actions = [fault(inputs, 'front', 'eio'), start(), clients, wait]
        if case == 'original-root-unlaunched-refusal':
            if not inputs['original_assertions']:
                raise RuntimeError('ORIGINAL_UNLAUNCHED_FULL_REFUSAL_ASSERTIONS_REQUIRED')
            required_kinds = []
        else:
            required_kinds = ['HANDOFF_ABORT', 'FRONT_RETAINED_ESCROW']
    elif case == 'original-root-transfer-abandon':
        actions = [start(), fault(inputs, 'worker', 'eio'), clients, wait]
        required_kinds = ['ABANDON']
    elif case in ('original-root-crash-entry', 'original-root-crash-exit-lost-ack', 'original-root-readback-uncertain'):
        effect = ('kill-entry' if case == 'original-root-crash-entry' else
                  'kill-exit' if case == 'original-root-crash-exit-lost-ack' else 'corrupt-readback-exit')
        actions = [start(), fault(inputs, 'worker', effect), clients, wait]
        required_kinds = ['UNKNOWN']
        controls = ['uncertain'] if case == 'original-root-readback-uncertain' else []
    elif case == 'original-root-exact-retry':
        actions = [start(), clients, wait, {'kind': 'retry', **inputs['retry']}]
        controls = ['retry']
    elif case == 'original-root-stale-cas':
        actions = [start(), clients, wait, {'kind': 'cas-stale', **inputs['stale']}]
        controls = ['cas-stale']
    elif case in DUPLEX_CASES:
        relay = client(inputs, 'relay', True)
        if DUPLEX_CASES[case] != 'gap-write':
            relay['expected_error'] = 'CLIENT_ORIGINAL_RESPONSE_EOF_WITHOUT_RESULT'
        actions = [start(), {'kind': 'wait-custody-ack', 'timeout': timeout}, relay, clients, wait]
        required_kinds = ['REQUEST_QUEUED', 'REQUEST_TRANSFER_INTENT', 'REQUEST_INTAKE']
    elif case == 'original-multiroot-carrier-relay':
        actions = [start(), {'kind': 'wait-custody-ack', 'timeout': timeout},
            client(inputs, 'relay', False), {'kind': 'transfer-readers', 'timeout': timeout}, clients, wait,
            client(inputs, 'next-root', False), {'kind': 'wait-custody-ack', 'timeout': timeout},
            client(inputs, 'next-relay', True), clients, wait]
        required_kinds = ['WORKER_REATTACHED', 'RECONCILED', 'REQUEST_INTAKE', 'DRAIN_INTAKE']
        controls = ['carry']
    else:
        # All original source methods and their original environment/timeouts
        # are exercised in their independent qualified processes, never mocked.
        if not inputs['original_assertions']:
            raise RuntimeError('ORIGINAL_RETAINED_FULL_ASSERTION_CORPUS_REQUIRED')
    return {'startup_descriptor': inputs['startup_descriptor'], 'observer': inputs['observer'],
        'result_directory': inputs['result_directory'], 'timeout': timeout, 'actions': actions,
        'original_assertions': inputs['original_assertions'], 'required_kinds': required_kinds,
        'required_controls': controls, 'required_subject_cases': subjects,
        'capture_paths': inputs['capture_paths'],
        'duplex_control': inputs['duplex_control'] if case in DUPLEX_CASES else None,
        'reader_control': inputs['reader_control'] if case in READER_CASES else None}


def bind(inputs):
    if set(inputs['cases']) != set(CASE_IDS):
        raise RuntimeError('ORIGINAL_COMPLETE_DETERMINISTIC_CORPUS_REQUIRED')
    return {name: recipe(name, inputs['cases'][name]) for name in CASE_IDS}

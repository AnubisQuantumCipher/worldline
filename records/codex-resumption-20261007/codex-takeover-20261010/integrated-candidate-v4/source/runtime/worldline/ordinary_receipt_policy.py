"""Owned original ordinary policy transport; no Python policy fallback.

Unicode strip/casefold and str(kind) are original field observations, not a
roster decision. Full SQL rows and original file bytes remain independently
captured; native code decides schema, joins, replay, prefix and actual write.
Ordinary authored intent is the original API, not external source authenticity.
"""
from __future__ import annotations
import ctypes
import json
import types
from dataclasses import fields
from .core import Core
from .errors import CoreUnavailable, WorldlineError
from .operation_capture import archive

_REASONS = ('READY', 'MALFORMED_INPUT', 'NEEDS_DAEMON_ACCOUNT', 'RESERVED_ACTOR',
            'RESERVED_KIND', 'INVALID_SCHEMA', 'INVALID_RECEIPT', 'REQUESTER_MISMATCH',
            'RECEIPT_PREDECESSOR_MISMATCH', 'HISTORY_INVALID',
            'COMPLETE_PREFIX_CHANGED', 'ACTUAL_WRITE_MISMATCH', 'PEER_OBSERVATION_REQUIRED',
            'CLAIM_OBSERVATION_REQUIRED', 'KIND_OBSERVATION_REQUIRED',
            'CAPTURED_PREDECESSOR_MISMATCH', 'CAPTURED_HEAD_MISMATCH',
            'READY_MUTATING', 'TRUTH_OBSERVATION_REQUIRED', 'ROUTE_OBSERVATION_MISMATCH',
            'ROW_COLUMNS_MISMATCH', 'SCHEMA_OBSERVATION_REQUIRED',
            'READY_AUTHORED', 'RECEIPT_KEY_OBSERVATION_REQUIRED',
            'RECEIPT_ALLOWED_KEYS_REQUIRED', 'RECEIPT_KEYS_REQUIRED',
            'RECEIPT_PREDECESSOR_OBSERVATION_REQUIRED')
_COLUMN_NAMES = ('event_id', 'world_instance', 'kind', 'actor', 'tool', 'reason',
                 'path_b64', 'path_display', 'line_start', 'line_end',
                 'receipt_id', 'transaction_id', 'previous_receipt')

def _decide(core, mode, packet):
    try:
        version = core._lib.wl_ordinary_receipt_policy_version_v35
        decide = core._lib.wl_ordinary_receipt_policy_decide_v35
    except AttributeError as exc:
        raise CoreUnavailable('selected kernel lacks original ordinary receipt policy') from exc
    raw = archive(packet)
    count = len(raw)
    if ctypes.c_size_t(count).value != count or ctypes.c_int64(count).value != count:
        raise CoreUnavailable('ordinary policy archive extent unavailable')
    owned = (ctypes.c_ubyte * count).from_buffer_copy(raw)
    version.argtypes, version.restype = [], ctypes.c_uint32
    decide.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint8]
    decide.restype = ctypes.c_int
    if version() != 35:
        raise CoreUnavailable('ordinary receipt policy ABI version differs')
    result = int(decide(owned, count, mode))
    if not 0 <= result < len(_REASONS):
        raise CoreUnavailable('ordinary receipt policy transport refused', status=result)
    return _REASONS[result]
def verify_columns(core, kind, row, payload, raw, columns, previous):
    """Native differences at the original verifier's row-comparison point."""
    from .core import hash_id
    try:
        version = core._lib.wl_ordinary_receipt_policy_version_v35
        verify = core._lib.wl_ordinary_receipt_verify_history_v35
    except AttributeError as exc:
        raise CoreUnavailable('selected kernel lacks complete ordinary column verification') from exc
    packet = {'kind': kind, 'sql': dict(row), 'payload': payload, 'raw': raw,
              'columns': columns, 'previous': hash_id(previous)}
    encoded = archive(packet)
    count = len(encoded)
    if ctypes.c_size_t(count).value != count or ctypes.c_int64(count).value != count:
        raise CoreUnavailable('ordinary column verification extent unavailable')
    owned = (ctypes.c_ubyte * count).from_buffer_copy(encoded)
    differences = ctypes.c_uint32()
    version.argtypes, version.restype = [], ctypes.c_uint32
    verify.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32)]
    verify.restype = ctypes.c_int
    if version() != 35:
        raise CoreUnavailable('ordinary receipt policy ABI version differs')
    result = int(verify(owned, count, ctypes.byref(differences)))
    if result not in (0, 20) or differences.value >> len(_COLUMN_NAMES):
        raise CoreUnavailable('ordinary column verification refused', status=result)
    if (result == 0) != (differences.value == 0):
        raise CoreUnavailable('ordinary column verification disposition differs from native mask')
    return sorted(name for bit, name in enumerate(_COLUMN_NAMES)
                  if differences.value & (1 << bit))


def reserved_claim(event, *, core=None):
    core = Core() if core is None else core
    actor = event.get('actor')
    packet = {'actor_source': _identity(actor),
              'actor_original': str.encode(actor, 'utf-8', 'surrogatepass')
              if isinstance(actor, str) else None,
              'actor_normalized': actor.strip().casefold().encode('utf-8', 'surrogatepass')
              if isinstance(actor, str) else None}
    result = _decide(core, 1, packet)
    if result == 'KIND_OBSERVATION_REQUIRED':
        kind = str(event.get('kind', 'event'))
        packet['kind_original'] = kind.encode('utf-8', 'surrogatepass')
        packet['kind_normalized'] = kind.strip().casefold().encode('utf-8', 'surrogatepass')
        result = _decide(core, 1, packet)
    if result == 'RESERVED_ACTOR':
        return f"actor {actor!r} is reserved for WORLDLINE and the operator"
    if result == 'RESERVED_KIND':
        return f"kind {kind!r} is reserved for WORLDLINE's own records"
    if result != 'READY':
        raise CoreUnavailable('ordinary reserved claim input refused', reason=result)
    return None

def _source_text(value):
    return str.__str__(value) if isinstance(value, str) else None

def _identity(value):
    kind = type(value)
    # Read the genuine built-in type descriptors, not custom metaclass hooks.
    # Descriptive module labels are not an original registration domain gate.
    module = type.__dict__['__module__'].__get__(kind)
    name = type.__dict__['__qualname__'].__get__(kind)
    return {'identity': id(value), 'module': _source_text(module), 'class': _source_text(name)}

def _metadata_observation(value):
    result = _identity(value)
    if type(value) in (type(None), bool, int, float, str, bytes):
        return {**result, 'form': 'value', 'value': value, 'truth': None}
    if type(value) in (list, tuple, dict, set, frozenset, bytearray):
        return {**result, 'form': 'extent', 'value': len(value), 'truth': None}
    # Arbitrary original register metadata retains its live truth protocol.
    # Do not call __bool__/__len__ during the other field's policy stage.
    return {**result, 'form': 'protocol', 'value': None, 'truth': None}

def _handler_observation(handler):
    function = handler.__func__ if type(handler) is types.MethodType else handler
    owner = handler.__self__ if type(handler) is types.MethodType else None
    is_function = type(function) in (types.FunctionType, types.BuiltinFunctionType)
    code = function.__code__ if type(function) is types.FunctionType else None
    return {**_identity(handler), 'function_identity': id(function),
            'owner_identity': None if owner is None else id(owner),
            'code_identity': None if code is None else id(code),
            'handler_module': _source_text(function.__module__) if is_function else None,
            'handler_name': _source_text(function.__qualname__) if is_function else None}

def route_source_observation(daemon, operation, selected):
    """Acquire the whole actual registered metadata roster, not an op DTO.

    This exporter is a live boundary observation, never standalone authority.
    Every original dataclass field is enrolled, with actual object/handler links.
    The selected registration is the same object subsequently invoked by daemon.
    """
    rows = []
    for name, original in daemon._operations.items():
        observed = {}
        for field in fields(original):
            value = getattr(original, field.name)
            observed[field.name] = (_handler_observation(value) if field.name == 'handler'
                                    else _metadata_observation(value))
        rows.append({**_identity(original),
                     'name': str.__str__(name) if isinstance(name, str) else None,
                     'key': _metadata_observation(name), 'fields': observed})
    registrations = [{'key_identity': id(name), 'identity': id(original),
                      'handler_identity': id(original.handler)}
                     for name, original in daemon._operation_registrations]
    return {'operation': operation, 'routes': rows, 'registrations': registrations,
            'selected': {'identity': id(selected), 'handler_identity': id(selected.handler)},
            'peer_uid': None, 'daemon_uid': None}

def _route_decide(core, mode, daemon, operation, selected, field):
    packet = route_source_observation(daemon, operation, selected)
    result = _decide(core, mode, packet)
    if result == 'TRUTH_OBSERVATION_REQUIRED':
        # The native decoder selected the original protocol field. This is the
        # actual supported live truth boundary; exceptions keep their old order.
        original = getattr(selected, field)
        observed = bool(original)
        for row in packet['routes']:
            if row['identity'] == id(selected):
                row['fields'][field]['truth'] = observed
        result = _decide(core, mode, packet)
    return result, packet

def owner_request(core, daemon, operation, selected, peer_observation):
    result, packet = _route_decide(core, 0, daemon, operation, selected, 'owner_only')
    if result == 'PEER_OBSERVATION_REQUIRED':
        packet['peer_uid'], packet['daemon_uid'] = peer_observation()
        result = _decide(core, 0, packet)
    if result == 'NEEDS_DAEMON_ACCOUNT':
        raise WorldlineError('OPERATION_NEEDS_DAEMON_ACCOUNT',
            f'{operation} moves directories between the operator and the store; '
            'a client of a dedicated-account daemon cannot request it')
    if result != 'READY':
        raise CoreUnavailable('ordinary owner policy input refused', reason=result)
def mutating_request(core, daemon, operation, selected):
    result, _packet = _route_decide(core, 7, daemon, operation, selected, 'mutating')
    if result not in ('READY', 'READY_MUTATING'):
        raise CoreUnavailable('ordinary mutation policy input refused', reason=result)
    return result == 'READY_MUTATING'

def actual_requester(store):
    """Acquire the original selected principal/scope, not a supplied requester.

    Native journal.load replays the full actual source/context before selecting
    an operation row. OwnerCanonicalScope uses its original owner journal bridge,
    not an invented operation-row lookup. The original metadata helper owns both.
    """
    from .protected_operations import CanonicalOperationPrincipal, canonical_metadata
    principal = getattr(store, 'canonical_operation_principal', None)
    if principal is None:
        return None
    if (type(principal) is not CanonicalOperationPrincipal or principal.store is not store
            or principal.lease.store is not store
            or getattr(principal.lease, 'canonical_operation_principal', None) is not principal):
        raise WorldlineError('OPERATION_PRINCIPAL_UNAUTHENTICATED',
                            'actual selected protected operation principal required')
    principal.intact()
    principal.journal.load()
    return canonical_metadata(store)

def _schema_decide(core, mode, packet, original):
    source = {**_metadata_observation(original), 'not_one': None}
    packet['schema_metadata'] = source
    result = _decide(core, mode, packet)
    if result == 'SCHEMA_OBSERVATION_REQUIRED':
        # Original `if schemaVersion != 1`: observe the actual live comparison
        # protocol, including its truth conversion and exact exception order.
        source['not_one'] = bool(original != 1)
        result = _decide(core, mode, packet)
    return result, source


def event_policy(core, event, authored):
    packet = {'payload': {}, 'authored_metadata': _metadata_observation(authored)}
    result, schema_source = _schema_decide(core, 2, packet, event.get('schemaVersion'))
    if result == 'TRUTH_OBSERVATION_REQUIRED':
        packet['authored_metadata']['truth'] = bool(authored)
        result = _decide(core, 2, packet)
    if result == 'INVALID_SCHEMA':
        raise WorldlineError('INVALID_SCHEMA', 'causal event schemaVersion must be literal 1')
    if result == 'CLAIM_OBSERVATION_REQUIRED':
        reason = reserved_claim(event, core=core)
        if reason is not None:
            raise WorldlineError('RESERVED_EVENT_CLAIM', f'causal event refused: {reason}',
                                 {'actor': event.get('actor'), 'kind': event.get('kind')})
        result = 'READY'
    if result not in ('READY', 'READY_AUTHORED'):
        raise CoreUnavailable('ordinary event policy input refused', reason=result)
    return result == 'READY_AUTHORED', schema_source

def receipt_schema(core, receipt):
    result, source = _schema_decide(core, 2,
        {'payload': {}, 'authored_metadata': _metadata_observation(True)},
        receipt.get('schemaVersion'))
    if result == 'INVALID_SCHEMA':
        raise WorldlineError('INVALID_SCHEMA', 'receipt schemaVersion must be literal 1')
    if result not in ('READY', 'READY_AUTHORED'):
        raise CoreUnavailable('ordinary receipt schema input refused', reason=result)
    return source

def receipt_predecessor(core, original, previous_row):
    row = None if previous_row is None else dict(previous_row)
    expected = None if row is None else row['receipt_id']
    source = {**_metadata_observation(original), 'expected': expected, 'not_previous': None}
    packet = {'previous_row': row, 'predecessor_source': source}
    result = _decide(core, 10, packet)
    if result == 'RECEIPT_PREDECESSOR_OBSERVATION_REQUIRED':
        source['not_previous'] = bool(original != expected)
        result = _decide(core, 10, packet)
    if result == 'RECEIPT_PREDECESSOR_MISMATCH':
        raise WorldlineError('RECEIPT_PREDECESSOR_MISMATCH', 'receipt does not name the current predecessor',
                            {'expected': expected, 'supplied': original})
    if result != 'READY':
        raise CoreUnavailable('ordinary receipt predecessor source refused', reason=result)
    return packet


def receipt_policy(core, receipt, requester, schema_source):
    # Field names are a complete type/value observation roster, not dictionary
    # keys in the archive grammar. Unrelated values remain for serialization.
    required = {'schemaVersion', 'receiptId', 'previousReceipt', 'parentWorld', 'candidateWorld',
                'baseState', 'candidateDelta', 'foreignWorldContamination', 'mergeSet',
                'invariantPreservation', 'atomicCollapse', 'beforeRoot', 'afterRoot',
                'transactionId', 'nonClaims'}
    optional = {'evidenceBinding'}
    fields = {}
    if requester is not None:
        fields['requesterBinding'] = receipt.get('requesterBinding')
        optional.add('requesterBinding')
    observed_sets = {'required_subset': None, 'allowed_subset': None, 'allowed_keys': None,
                     'receipt_identity': id(receipt), 'required_set_identity': None,
                     'allowed_set_identity': None}
    packet = {'payload': fields, 'requester': requester, 'schema_metadata': schema_source,
              'receipt_keys': None, 'set_observation': observed_sets}
    first = second = None
    result = _decide(core, 3, packet)
    while result in ('RECEIPT_KEYS_REQUIRED', 'RECEIPT_ALLOWED_KEYS_REQUIRED',
                     'RECEIPT_KEY_OBSERVATION_REQUIRED'):
        if result == 'RECEIPT_KEYS_REQUIRED':
            first = set(receipt)
            packet['receipt_keys'] = [_metadata_observation(key) for key in first]
            observed_sets['required_set_identity'] = id(first)
        elif result == 'RECEIPT_ALLOWED_KEYS_REQUIRED':
            second = set(receipt)
            observed_sets['allowed_keys'] = [_metadata_observation(key) for key in second]
            observed_sets['allowed_set_identity'] = id(second)
        elif second is None:
            observed_sets['required_subset'] = required <= first
        else:
            observed_sets['allowed_subset'] = second <= required | optional
        result = _decide(core, 3, packet)
    if result == 'INVALID_SCHEMA':
        raise WorldlineError('INVALID_SCHEMA', 'receipt schemaVersion must be literal 1')
    if result == 'REQUESTER_MISMATCH':
        raise WorldlineError('INVALID_RECEIPT', 'authentic operation scope required')
    if result == 'INVALID_RECEIPT':
        # Native membership decided rejection. Preserve original repeated
        # set/sorting detail projection and its original exception stage.
        raise WorldlineError('INVALID_RECEIPT', 'collapse receipt fields do not match schema',
                            {'missing': sorted(required - set(receipt)), 'extra': sorted(set(receipt) - required)})
    if result != 'READY':
        raise CoreUnavailable('ordinary receipt policy input refused', reason=result)

def material(store, kind):
    table = 'receipts' if kind == 'receipts' else 'causal_events'
    result = []
    for row in store._connection.execute(
            f'SELECT rowid AS native_rowid,* FROM {table} ORDER BY rowid').fetchall():
        sql = dict(row)
        rowid = sql.pop('native_rowid')
        raw = store.read_canonical(kind, sql['canonical_path'], chain_hash=sql['chain_hash'])
        payload = json.loads(raw.decode('utf-8'))
        result.append({'sql': sql, 'raw': raw, 'payload': payload, 'rowid': rowid})
    return result

def append_preflight(store, kind, payload, raw, previous, head, requester, schema_source, predecessor=None):
    requester = actual_requester(store)
    packet = {'kind': kind, 'payload': json.loads(raw.decode('utf-8')), 'requester': requester,
              'old': material(store, kind), 'expected': raw,
              'expected_previous': previous, 'expected_head': head,
              'live_schema': schema_source, 'connection_identity': id(store._connection),
              'store_identity': id(store)}
    if kind == 'receipts':
        packet.update(predecessor)
    _append_result(store, _decide(store.core, 4, packet), packet)
    return packet

def append_postflight(store, packet, cursor):
    # The unchanged real SQLite INSERT is the actual native affinity/adaptation
    # interpreter. Its output is not an approximate CAST or copied plan.
    # Acquire the cursor's actual row separately from full independent readback.
    table = 'receipts' if packet['kind'] == 'receipts' else 'causal_events'
    lastrowid = cursor.lastrowid
    source = store._connection.execute(
        f'SELECT rowid AS native_rowid,* FROM {table} WHERE rowid=?', (lastrowid,)).fetchone()
    if source is None:
        raise CoreUnavailable('original SQLite write row is unavailable after INSERT')
    sql = dict(source)
    rowid = sql.pop('native_rowid')
    ddl = store._connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    schema = {'table': table, 'ddl': None if ddl is None else ddl['sql'],
              'table_list': [dict(row) for row in store._connection.execute('PRAGMA table_list').fetchall()],
              'columns': [dict(row) for row in store._connection.execute(f'PRAGMA table_xinfo({table})').fetchall()]}
    write = {'cursor': _identity(cursor), 'lastrowid': lastrowid, 'rowid': rowid, 'sql': sql,
             'schema': schema, 'connection_identity': id(store._connection), 'store_identity': id(store)}
    actual = {**packet, 'sqlite_write': write, 'current': material(store, packet['kind'])}
    _append_result(store, _decide(store.core, 9, actual), actual)
    return actual

def _append_result(store, result, packet):
    if result == 'RECEIPT_PREDECESSOR_MISMATCH':
        old = packet['old']
        expected = None if not old else old[-1]['sql']['receipt_id']
        raise WorldlineError('RECEIPT_PREDECESSOR_MISMATCH', 'receipt does not name the current predecessor',
                            {'expected': expected, 'supplied': packet['payload']['previousReceipt']})
    if result == 'REQUESTER_MISMATCH':
        if packet['kind'] == 'events':
            from .protected_startup import StartupRefusal
            raise StartupRefusal('OPERATION_CANONICAL_REQUESTER_MISMATCH')
        raise WorldlineError('INVALID_RECEIPT', 'authentic operation scope required')
    if result != 'READY':
        raise WorldlineError('OPERATION_ORIGINAL_FULL_CHAIN_NATIVE_REFUSED',
                            'complete original canonical append refused', {'reason': result})

def retained_material(kind, retained):
    """Preserve the original complete SQL/raw pair capture without selection."""
    rows = retained[kind] if type(retained) is dict else retained
    return [{'sql': dict(sql), 'raw': raw, 'payload': json.loads(raw.decode('utf-8'))}
            for sql, raw in rows]

def native_acknowledge(kind, before_material, actual_material, expected_raw,
                       expected_head, expected_requester=None, *, core):
    before = retained_material(kind, before_material)
    actual = retained_material(kind, actual_material)
    return _decide(core, 5, {
        'kind': kind, 'old': before, 'current': actual,
        'payload': json.loads(expected_raw.decode('utf-8')),
        'expected': expected_raw, 'expected_head': expected_head,
        'requester': expected_requester,
    })

def native_preflight_head(kind, before_material, expected_previous, *, core):
    return _decide(core, 6, {
        'kind': kind, 'old': retained_material(kind, before_material),
        'expected_previous': expected_previous,
    })

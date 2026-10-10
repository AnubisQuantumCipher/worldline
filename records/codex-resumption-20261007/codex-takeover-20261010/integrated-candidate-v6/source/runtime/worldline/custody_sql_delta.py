"""Mechanical SQL consumer of the native Legal/Next result, never an authority."""
import struct
from .protected_startup import require

_KEYS = {'schema', 'event', 'roots', 'subjects', 'alternatives', 'blobs', 'head', 'head_message'}
_COLUMNS = {
 'root_state': ('generation','operation','phase','before_unknown','owners_open','abort_class','launched',
                'closure_ns','closure_outer','closure_raw','witness','settled','released_unlaunched',
                'unknown_cause','reattach_epoch','head_event'),
 'subject_state': ('generation','subject_kind','subject','subgeneration','phase','mode','position','carried_from','head_event'),
 'alternatives': ('generation','operation','subject_kind','subject','subgeneration','alternative_set','event_id'),
 'blobs': ('sha256','kind','bytes'),
 'head': ('name','head_kind','event_id','origin','mac'),
 'events': ('event_id','previous','generation','operation','subject_kind','subject','subgeneration','kind','actor','record','base','mac')}
_PRIMARY = {'root_state': 1, 'subject_state': 3, 'alternatives': 6, 'blobs': 1, 'head': 1}

def unhex(word):
    require(type(word) is str, 'CUSTODY_NATIVE_DELTA_HEX_TYPE')
    try: raw = bytes.fromhex(word)
    except ValueError as error: raise ValueError('custody native delta malformed hex') from error
    require(raw.hex() == word, 'CUSTODY_NATIVE_DELTA_HEX_CANONICAL')
    return raw

def cell(value):
    require(type(value) is list and len(value) == 3 and type(value[0]) is int and
            type(value[1]) is bool, 'CUSTODY_NATIVE_DELTA_CELL_LAYOUT')
    tag, negative, word = value; raw = unhex(word)
    if tag == 0:
        require(not negative and not raw, 'CUSTODY_NATIVE_DELTA_NULL_LAYOUT'); return None
    if tag == 1:
        require(not raw or raw[-1] != 0, 'CUSTODY_NATIVE_DELTA_INTEGER_ENCODING')
        magnitude = int.from_bytes(raw, 'little')
        require(not negative or magnitude != 0, 'CUSTODY_NATIVE_DELTA_NEGATIVE_ZERO')
        return -magnitude if negative else magnitude
    require(not negative, 'CUSTODY_NATIVE_DELTA_NONINTEGER_SIGN')
    if tag == 2: return raw.decode('utf-8')
    if tag == 3: return raw
    if tag == 4:
        # Original scoped REAL encoding is opaque binary64 network-order bits.
        # Do not invent finite/isfinite or negative-zero policy here.
        require(len(raw) == 8, 'CUSTODY_NATIVE_DELTA_REAL_BINARY64_LAYOUT')
        return struct.unpack('!d', raw)[0]
    require(False, 'CUSTODY_NATIVE_DELTA_UNKNOWN_STORAGE_CLASS')

def row(value, count):
    require(type(value) is list and len(value) == count, 'CUSTODY_NATIVE_DELTA_WHOLE_ROW_REQUIRED')
    return tuple(cell(item) for item in value)

def decode(delta):
    require(type(delta) is dict and set(delta) == _KEYS and
            delta['schema'] == 'worldline.custody-native-delta-v2', 'CUSTODY_NATIVE_DELTA_SCHEMA')
    result = {'event': row(delta['event'], 12), 'head': row(delta['head'], 5),
              'head_message': unhex(delta['head_message'])}
    for name, count in (('roots',16),('subjects',9),('alternatives',7),('blobs',3)):
        require(type(delta[name]) is list, 'CUSTODY_NATIVE_DELTA_ROSTER_REQUIRED')
        result[name] = tuple(row(value, count) for value in delta[name])
    return result

def _upsert(db, table, values):
    columns = _COLUMNS[table]; keys = columns[:_PRIMARY[table]]
    existing = db.execute('SELECT ' + ','.join(columns) + ' FROM ' + table + ' WHERE ' +
                         ' AND '.join(name + ' IS ?' for name in keys), values[:len(keys)]).fetchall()
    require(len(existing) <= 1, 'CUSTODY_NATIVE_DELTA_AMBIGUOUS_KEY')
    if existing == [values]: return
    if not existing:
        db.execute('INSERT INTO ' + table + '(' + ','.join(columns) + ') VALUES (' +
                   ','.join('?' for _ in columns) + ')', values)
    else:
        changed = db.execute('UPDATE ' + table + ' SET ' + ','.join(name + '=?' for name in columns[len(keys):]) +
                             ' WHERE ' + ' AND '.join(name + ' IS ?' for name in keys),
                             values[len(keys):] + values[:len(keys)]).rowcount
        require(changed == 1, 'CUSTODY_NATIVE_DELTA_ACTUAL_SQL_CAS_CHANGED')

def apply(db, delta):
    """Requires caller's retained BEGIN IMMEDIATE and native ReadyApply dispatch."""
    require(db.in_transaction and db.execute('PRAGMA foreign_keys').fetchall() == [(1,)],
            'CUSTODY_NATIVE_DELTA_ACTUAL_FK_TRANSACTION_REQUIRED')
    values = decode(delta)
    columns = _COLUMNS['events']
    db.execute('INSERT INTO events(' + ','.join(columns) + ') VALUES (' + ','.join('?' for _ in columns) + ')',
               values['event'])
    # Keep old rows and their rowids intact; do not replace/delete histories or
    # disable/defer their foreign keys. Every changed value comes from native.
    for name, table in (('blobs','blobs'),('roots','root_state'),('subjects','subject_state'),('alternatives','alternatives')):
        for value in values[name]: _upsert(db, table, value)
    _upsert(db, 'head', values['head'])
    return values

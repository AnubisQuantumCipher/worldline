"""Authentic owner capture -> native retained-v1 operand bytes, no authority.

This producer creates no state, request, acknowledgement, genesis or phase.
It does not call a native export until the sole existing ABI is integrated.
"""
from dataclasses import dataclass
from pathlib import Path
from .protected_startup import require,private_bytes,digest
from .root_worker_current_state import capture_current_roster
from .root_worker_codec import archive,restore_archive
from .root_worker_journal import SCHEMA

@dataclass(frozen=True)
class RetainedInputs:
    arena:bytes
    key:tuple
    genesis_archive:tuple
    head_archive:tuple
    genesis_rows:tuple
    event_rows:tuple
    head_rows:tuple
    # Whole captures remain lossless bytes, not a projected/filtered roster.
    owner_capture_archive:bytes
    gate_raw:bytes
    run_database_archive:bytes
    # Records missing custody-v2 fields are deliberately NOT upgraded.
    schema:str='worldline.retained-root-custody-v1-native-inputs'

def capture_retained_inputs(owner):
    """No supplied snapshot: only the authentic stable owner producer is called."""
    capture=capture_current_roster(owner)
    current=capture['current']
    entries={entry['path']:entry for entry in current['paths']}
    def retained(path):
        word=str(path)
        require(word in entries,'ROOT_RETAINED_REQUIRED_PROVISIONED_INPUT_ABSENT')
        return entries[word]
    journal=owner.custody_journal
    root=Path(owner.spec['paths']['authority_root'])
    gate=retained(root/'authority/gate/state/journal.json')
    run=retained(root/'authority/resource/run-state-v1/ledger.sqlite')
    custody=retained(journal.path)
    require('logical_database' in run and 'logical_database' in custody,
            'ROOT_RETAINED_FULL_DATABASE_CAPTURE_ABSENT')
    require('logical_database' not in gate,'ROOT_RETAINED_GATE_FILE_KIND_CHANGED')
    database=custody['logical_database']
    tables={table['name']:table for table in database['tables']}
    require(set(tables)==set(SCHEMA),'ROOT_RETAINED_CUSTODY_TABLE_ROSTER_CHANGED')
    def rows(name):
        table=tables[name]
        require(tuple((col[1],col[2]) for col in table['columns'])==SCHEMA[name],
                'ROOT_RETAINED_CUSTODY_COLUMN_ROSTER_CHANGED')
        require(table['query']=='SELECT rowid,* FROM "'+name+'" ORDER BY rowid',
                'ROOT_RETAINED_CUSTODY_ROW_ORDER_CHANGED')
        require(all(len(row)==len(SCHEMA[name])+1 for row in table['rows']),
                'ROOT_RETAINED_CUSTODY_ROW_EXTENT_CHANGED')
        return tuple(row[1:] for row in table['rows'])
    # Re-read the original protected issuer file; do not substitute a digest or
    # caller-authenticated flag for the complete key. Owner/source remains live.
    key=private_bytes(root/'authority/issuer/state/issuer-key.bin')
    require(key==journal.key and digest(key)==journal.genesis['issuer_key_sha256'],
            'ROOT_RETAINED_ISSUER_KEY_CHANGED')
    require(retained(journal.genesis_path)['raw']==private_bytes(journal.genesis_path),
            'ROOT_RETAINED_GENESIS_FILE_CHANGED')
    arena=bytearray()
    def put(value):
        require(type(value) is bytes,'ROOT_RETAINED_NATIVE_BYTES_REQUIRED')
        span=(len(arena)+1,len(value));arena.extend(value);return span
    def text(value):
        require(type(value) is str,'ROOT_RETAINED_SQL_TEXT_REQUIRED')
        return put(value.encode('utf-8','surrogatepass'))
    key_span=put(key)
    genesis_span=put(archive(journal.genesis))
    genesis_rows=tuple((text(name),put(value)) for name,value in rows('genesis'))
    events=[]
    for event_id,previous,operation,kind,raw,mac in rows('events'):
        require(type(raw) is bytes,'ROOT_RETAINED_SQL_RECORD_BYTES_REQUIRED')
        record=restore_archive(raw)
        base={'previous':previous,'operation':operation,'kind':kind,'record':record}
        # Field order exactly matches the native Event_Row declaration.
        events.append((text(event_id),text(previous),text(operation),text(kind),
                       put(raw),text(mac),put(archive(base))))
    raw_heads=rows('head')
    heads=tuple((text(name),text(event_id),text(mac)) for name,event_id,mac in raw_heads)
    # Do not derive a head from events or manufacture an empty-history head.
    # Cardinality is an original journal requirement, not a new lifecycle rule.
    require(len(raw_heads)==1,'ROOT_RETAINED_CURRENT_HEAD_ABSENT_OR_SPLIT')
    head_span=put(archive({'head':raw_heads[0][1],'genesis':journal.genesis}))
    owner.intact()
    return RetainedInputs(bytes(arena),key_span,genesis_span,head_span,
        genesis_rows,tuple(events),heads,archive(capture),gate['raw'],archive(run))

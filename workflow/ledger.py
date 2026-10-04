"""Proof-repair burn-down ledger (lead working record; states require evidence pointers).

Usage:
  ledger.py seed DIAGNOSTIC_MAP_JSON          create ledger.json from a complete diagnostic map (create-only)
  ledger.py set ID STATE EVIDENCE_PATH [NOTE] move an item; EVIDENCE_PATH must exist; history is append-only
  ledger.py set-many IDS_FILE STATE EVIDENCE_PATH [NOTE]   the same for every id listed (one per line)
  ledger.py facet IDS_FILE FACET EVIDENCE_PATH [NOTE]    record an independent fact without moving the state:
                                              FACET is source_reviewed (in a GPT-6.1-qualified composition, recorded
                                              before engineering verification), deferred (owned by another packet) or
                                              adjudication (contract/reference text or tool-model item needing a reviewer ruling)
  ledger.py report                            counts per state and per class, plus facet counts
States, in order: OPEN, DRAFTED, ENGINEERING_VERIFIED, REVIEWED, STRICT_VERIFIED.
ENGINEERING_VERIFIED = the diagnostic is absent and the check proved in an adopted scratch-frame run (engineering-only).
REVIEWED = in a GPT-6.1-qualified composition. STRICT_VERIFIED = closed by the exact original strict command on the
reviewed integrated candidate. Only STRICT_VERIFIED plus final review closes an original obligation.
"""
from pathlib import Path
import collections, datetime, hashlib, json, os, sys
HERE = Path(__file__).resolve().parent
LEDGER = HERE / 'ledger.json'
STATES = ['OPEN', 'DRAFTED', 'ENGINEERING_VERIFIED', 'REVIEWED', 'STRICT_VERIFIED']
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(value):
    tmp = LEDGER.with_suffix('.tmp'); tmp.write_text(json.dumps(value, indent=1) + '\n'); os.replace(tmp, LEDGER)
def classify(entry):
    rule, message, sev = entry['rule'] or '', entry['message'] or '', entry['severity']
    if sev == 'error': return 'A_legality'
    if sev in ('low', 'medium', 'high'): return 'B_unproved'
    if 'Is_Valid' in message: return 'C5_bigint_validity'
    if 'reassociation' in rule or 'reassociation' in message: return 'C2_reassociation'
    if rule in ('contracts-recursive', 'numeric-variant'): return 'C3_recursive_contract'
    if 'unreachable' in message or rule == 'VC_DEAD_CODE': return 'C4_unreachable'
    if 'address-to-access' in rule: return 'C6_address_access'
    return 'C_other_warning'
verb = sys.argv[1]
if verb == 'seed':
    assert not LEDGER.exists(), 'ledger already seeded'
    source = Path(sys.argv[2]); data = json.loads(source.read_text())
    # Merge the console and generated .spark lanes of the same diagnostic (same location and message text).
    merged = collections.OrderedDict()
    for e in data['entries']:
        key = (e['file'], e['line'], e['col'], (e['message'] or '').strip())
        if key in merged:
            m = merged[key]
            m['occurrences'] = max(m['occurrences'], e['occurrences'])
            m['origins'] = sorted(set(m['origins']) | set(e['origins']))
            if m['rule'] == 'console':
                m['rule'] = e['rule']
            if m['severity'] == 'warning' and e['severity'] in ('error', 'low', 'medium', 'high'):
                m['severity'] = e['severity']
        else:
            merged[key] = dict(e)
    items = []
    for i, e in enumerate(merged.values()):
        items.append({'id': 'D%04d' % (i + 1), 'class': classify(e), 'severity': e['severity'], 'rule': e['rule'],
                      'file': e['file'], 'line': e['line'], 'col': e['col'], 'message': e['message'],
                      'occurrences': e['occurrences'], 'spec': e['spec'], 'state': 'OPEN',
                      'history': [{'at': now(), 'state': 'OPEN', 'evidence': str(source)}]})
    save({'schema': 'claude-proof-repair-ledger-v1', 'seeded_from': {'path': str(source),
          'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}, 'seeded_at': now(), 'items': items})
    print(json.dumps({'seeded': len(items)}))
elif verb == 'set':
    ident, state, evidence = sys.argv[2], sys.argv[3], Path(sys.argv[4]); note = sys.argv[5] if len(sys.argv) > 5 else ''
    assert state in STATES and evidence.exists(), 'state or evidence'
    value = json.loads(LEDGER.read_text())
    item = next(i for i in value['items'] if i['id'] == ident)
    item['state'] = state
    item['history'].append({'at': now(), 'state': state, 'evidence': str(evidence),
                            'evidence_sha256': hashlib.sha256(evidence.read_bytes()).hexdigest() if evidence.is_file() else None,
                            'note': note})
    save(value); print(json.dumps({'id': ident, 'state': state}))
elif verb in ('set-many', 'facet'):
    ids = [l.strip() for l in Path(sys.argv[2]).read_text().splitlines() if l.strip()]
    name, evidence = sys.argv[3], Path(sys.argv[4]); note = sys.argv[5] if len(sys.argv) > 5 else ''
    assert evidence.exists(), 'evidence'
    if verb == 'set-many':
        assert name in STATES, 'state'
    else:
        assert name in ('source_reviewed', 'deferred', 'adjudication'), 'facet'
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest() if evidence.is_file() else None
    value = json.loads(LEDGER.read_text())
    index = {i['id']: i for i in value['items']}
    assert len(set(ids)) == len(ids) and all(x in index for x in ids), 'ids'
    for x in ids:
        item = index[x]
        row = {'at': now(), 'evidence': str(evidence), 'evidence_sha256': digest, 'note': note}
        if verb == 'set-many':
            item['state'] = name; row['state'] = name
        else:
            item.setdefault('facets', {})[name] = row; row['facet'] = name
        item['history'].append(row)
    save(value); print(json.dumps({'updated': len(ids), verb: name}))
elif verb == 'report':
    value = json.loads(LEDGER.read_text())
    by_state = collections.Counter(i['state'] for i in value['items'])
    by_class = collections.defaultdict(collections.Counter)
    for i in value['items']: by_class[i['class']][i['state']] += 1
    print('total', len(value['items']), {s: by_state.get(s, 0) for s in STATES})
    for c in sorted(by_class): print(' ', c, dict(by_class[c]))
    facets = collections.Counter(f for i in value['items'] for f in i.get('facets', {}))
    print('facets', dict(facets))

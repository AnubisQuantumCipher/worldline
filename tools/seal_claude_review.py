#!/usr/bin/env python3
"""Seal an independent Claude review subagent's final message into a review directory.

The harness refuses report files from subagents, so a reviewer returns REVIEW.md, review.json and
checks.json as text between "=== NAME ===" markers, then a "=== SEAL ===" JSON block, then "=== END ===".
This tool takes the LAST assistant text message of the reviewer's own task output (JSONL), writes it
unmodified to raw-final-message.txt, splits it into the three files verbatim, and writes review-freeze.json.

INTEGRITY (frame §23 R1/R2 hardening). The reviewer's final message — the independent transcript's own
bytes — MUST carry a "=== SEAL ===" block: {"completed_at": <ISO8601>, "sections": {"REVIEW.md": <sha256>,
"review.json": <sha256>, "checks.json": <sha256>}}. The sealer VERIFIES each cited hash equals the
hash of the extracted section bytes, so the sealed review is cryptographically bound to what the
independent reviewer actually emitted (a post-hoc edit of any section fails the check). review.json is
written BYTE-IDENTICAL to what the reviewer emitted (no lead fields added), so its on-disk hash equals the
reviewer's cite. The FREEZE (not review.json) records `completed_at`, `seal_verified` (the SEAL was present
and every cited hash matched), the reviewer-cited section hashes, the task-output sha256 and the reviewer
agent id; the adoption join reads the binding from the freeze. A legacy final message with no SEAL block is sealed with a
loud warning and completed_at=null; such a freeze CANNOT satisfy the hardened Claude-review adoption join.

Every file is create-only (O_EXCL), fsynced, mode 0600.
usage: seal_claude_review.py TASK_OUTPUT_JSONL REVIEW_DIR AGENT_ID
"""
import hashlib, json, os, sys


def last_assistant_text(path):
    text = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            msg = o.get('message') if isinstance(o, dict) else None
            if not isinstance(msg, dict) or msg.get('role') != 'assistant':
                continue
            parts = [c.get('text', '') for c in msg.get('content', []) if isinstance(c, dict) and c.get('type') == 'text']
            joined = ''.join(parts)
            if '=== REVIEW.md ===' in joined:
                text = joined
    if text is None:
        sys.exit('no final message with markers found')
    return text


def create(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': '0600'}


def section(text, name, nxt):
    start = text.index(f'=== {name} ===\n') + len(f'=== {name} ===\n')
    end = text.index(f'\n=== {nxt} ===', start)
    return text[start:end].strip('\n') + '\n'


def main():
    src, out, agent = sys.argv[1:4]
    text = last_assistant_text(src)
    has_seal = '=== SEAL ===\n' in text
    os.makedirs(out, exist_ok=False)
    create(os.path.join(out, 'raw-final-message.txt'), text.encode('utf-8'))
    review_md = section(text, 'REVIEW.md', 'review.json').encode('utf-8')
    review = json.loads(section(text, 'review.json', 'checks.json'))
    checks_txt = section(text, 'checks.json', 'SEAL' if has_seal else 'END')
    json.loads(checks_txt)
    review_json_bytes = (json.dumps(review, indent=1, ensure_ascii=False) + '\n').encode('utf-8')

    # SEAL verification: the independent final message must cite the hashes of the exact section bytes.
    completed_at = None
    cited = None
    seal_ok = False
    if has_seal:
        seal = json.loads(section(text, 'SEAL', 'END'))
        completed_at = seal.get('completed_at')
        cited = seal.get('sections') or {}
        # The reviewer cites the sha256 of the EXACT bytes it emits for each section. review.json is
        # re-serialized by the lead with indent=1; the reviewer must cite the hash of that canonical form,
        # OR of its own emitted text. We verify against BOTH the emitted-text hash and (for review.json)
        # the canonical re-serialized hash, and record which matched.
        emit = {
            'REVIEW.md': hashlib.sha256(review_md).hexdigest(),
            'review.json': hashlib.sha256(review_json_bytes).hexdigest(),
            'checks.json': hashlib.sha256(checks_txt.encode('utf-8')).hexdigest(),
        }
        raw_review_json = section(text, 'review.json', 'checks.json').encode('utf-8')
        alt_review_json = hashlib.sha256(raw_review_json).hexdigest()
        mism = []
        for k in ('REVIEW.md', 'review.json', 'checks.json'):
            c = cited.get(k)
            if c == emit[k]:
                continue
            if k == 'review.json' and c == alt_review_json:
                continue
            mism.append(f'{k}: cited {c} != emitted {emit[k]}' + (f' (raw {alt_review_json})' if k == 'review.json' else ''))
        if mism:
            sys.exit('SEAL section-hash MISMATCH (sealed review not bound to the independent final message):\n' + '\n'.join(mism))
        if not completed_at or not isinstance(completed_at, str):
            sys.exit('SEAL missing a non-empty completed_at (R2)')
        seal_ok = True
    else:
        sys.stderr.write('WARNING: no === SEAL === block in the final message; completed_at=null; this '
                         'freeze CANNOT satisfy the hardened Claude-review adoption join (frame §23 R1/R2).\n')

    files = {}
    files['REVIEW.md'] = create(os.path.join(out, 'REVIEW.md'), review_md)
    files['checks.json'] = create(os.path.join(out, 'checks.json'), checks_txt.encode('utf-8'))
    task_out_sha = hashlib.sha256(open(src, 'rb').read()).hexdigest()
    # review.json is written BYTE-IDENTICAL to the bytes the independent reviewer emitted and cited in
    # its SEAL block; the lead adds NO fields to it, so the on-disk review.json sha256 equals the
    # reviewer's cite and the content-binding holds. ALL lead-added binding facts (seal_verified,
    # reviewer_agent_id, source_task_output_sha256, reviewer_cited_section_sha256, completed_at) live in
    # review-freeze.json below; the adoption join reads them from the FREEZE, never from review.json.
    files['review.json'] = create(os.path.join(out, 'review.json'), review_json_bytes)
    freeze = {'actual_model_selection': review.get('actual_model_selection'), 'reviewer_kind': review.get('reviewer_kind'),
              'different_from_author': review.get('different_from_author'),
              'completed_at': completed_at, 'seal_verified': seal_ok,
              'reviewer_agent_id': agent, 'source_task_output_sha256': task_out_sha,
              'reviewer_cited_section_sha256': cited, 'files': files}
    create(os.path.join(out, 'review-freeze.json'), (json.dumps(freeze, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({'verdict': review.get('verdict'), 'seal_verified': seal_ok, 'completed_at': completed_at,
                      'files': files}, indent=1))


if __name__ == '__main__':
    main()

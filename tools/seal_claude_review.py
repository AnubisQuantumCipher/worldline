#!/usr/bin/env python3
"""Seal an independent Claude review subagent's final message into a review directory.

The harness refuses report files from subagents, so a reviewer returns REVIEW.md, review.json and
checks.json as text between "=== NAME ===" markers. This tool takes the LAST assistant text message of
the reviewer's own task output (JSONL), writes it unmodified to raw-final-message.txt, splits it into
the three files verbatim, adds report_sha256 and checks to review.json (the only lead-computed fields),
and writes review-freeze.json last. Every file is create-only (O_EXCL), fsynced, mode 0600.

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
    os.makedirs(out, exist_ok=False)
    create(os.path.join(out, 'raw-final-message.txt'), text.encode('utf-8'))
    review_md = section(text, 'REVIEW.md', 'review.json').encode('utf-8')
    review = json.loads(section(text, 'review.json', 'checks.json'))
    checks_txt = section(text, 'checks.json', 'END')
    json.loads(checks_txt)
    files = {}
    files['REVIEW.md'] = create(os.path.join(out, 'REVIEW.md'), review_md)
    files['checks.json'] = create(os.path.join(out, 'checks.json'), checks_txt.encode('utf-8'))
    review['report_sha256'] = files['REVIEW.md']['sha256']
    review['checks'] = dict(path=os.path.join(out, 'checks.json'), **files['checks.json'])
    review['sealed_by'] = {'role': 'lead (claude-opus-5-5); verbatim transcription of the reviewer final message',
                           'reviewer_agent_id': agent, 'source_task_output': src,
                           'source_task_output_sha256': hashlib.sha256(open(src, 'rb').read()).hexdigest()}
    files['review.json'] = create(os.path.join(out, 'review.json'),
                                  (json.dumps(review, indent=1, ensure_ascii=False) + '\n').encode('utf-8'))
    freeze = {'actual_model_selection': review.get('actual_model_selection'), 'reviewer_kind': review.get('reviewer_kind'),
              'different_from_author': review.get('different_from_author'), 'files': files}
    create(os.path.join(out, 'review-freeze.json'), (json.dumps(freeze, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({'verdict': review.get('verdict'), 'files': files}, indent=1))


if __name__ == '__main__':
    main()

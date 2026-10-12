#!/usr/bin/env python3
"""Verify this archival package, not product correctness or campaign acceptance."""
import gzip, hashlib, json, pathlib, stat, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
def digest(stream):
    h=hashlib.sha256(); n=0
    while b:=stream.read(1024*1024): h.update(b); n+=len(b)
    return h.hexdigest(),n

def main():
    entries=json.loads((ROOT/'files.json').read_text())
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == set(entries)|{'files.json'}
    for name,e in entries.items():
        p=ROOT/name
        with p.open('rb') as f: h,n=digest(f)
        assert h==e['sha256'] and n==e['bytes'],name
    receipts=json.loads((ROOT/'copy-receipts.json').read_text())
    for r in receipts:
        with tempfile.TemporaryFile() as joined:
            for part in r['parts']:
                with (ROOT/part).open('rb') as f:
                    while b:=f.read(1024*1024):joined.write(b)
            joined.seek(0)
            if r['encoding']=='gzip':
                with gzip.GzipFile(fileobj=joined) as f:h,n=digest(f)
            else:h,n=digest(joined)
        assert (h,n)==(r['original_sha256'],r['original_bytes']),r['original_path']
    checkpoint=json.loads((ROOT/'checkpoint.json').read_text())
    for source in checkpoint['sources']:
        base=ROOT/source['path']; inv=json.loads((ROOT/f"source-{source['label']}-inventory.json").read_text())
        assert {str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}=={r['path'] for r in inv}
        for r in inv:
            p=base/r['path']
            with p.open('rb') as f:h,_=digest(f)
            mode='100755' if p.stat().st_mode&stat.S_IXUSR else '100644'
            assert h==r['sha256'] and mode==r['mode'],str(p)
    print(json.dumps({'package_integrity':'PASS','source_inventories':'PASS','original_evidence_recovery':'PASS','files':len(entries),'evidence_records':len(receipts),'product_acceptance':False}))

if __name__=='__main__':main()

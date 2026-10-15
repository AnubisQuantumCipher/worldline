#!/usr/bin/env python3
"""Fail-closed report structure/hash checker. Never grants product acceptance.

This validates supplied records, not the truth of a passed gate's semantic predicates.
A separate actual GPT-6.1 review must assess matching raw evidence against binding gates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
BINDING = ROOT / 'docs/phase1-acceptance.md'
STATUSES = {'PASSED', 'FAILED-OPEN', 'NOT PERFORMED'}
CLASSES = {'PROVED', 'MEASURED', 'TESTED', 'ASSUMED', 'UNVERIFIED'}
SHA = re.compile(r'^[0-9a-f]{64}$')
COMMIT = re.compile(r'^[0-9a-f]{40}$')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def roster():
    return re.findall(r'^\| ((?:G|A|O|C|F)[0-9]+) \|', BINDING.read_text(), re.M)

def inspect(report):
    errors=[]
    def require(ok, message):
        if not ok: errors.append(message)
    require(report.get('schema')=='worldline.phase1-final-gate-report.v1','unknown schema')
    frozen=report.get('frozen_source_commit')
    require(isinstance(frozen,str) and bool(COMMIT.fullmatch(frozen)),'missing full frozen source commit')
    require(report.get('binding_acceptance_sha256')==digest(BINDING),'binding file hash mismatch')
    require(report.get('independent_acceptance')=='NOT PERFORMED','independent acceptance must remain NOT PERFORMED')
    require(report.get('checker_scope')=='structure and artifact hashes only; semantic acceptance separate','checker boundary missing')
    limits=report.get('limits',{})
    require(limits.get('isolation_breach') and limits.get('imported_sparklib_proof_gap'),'required isolation/proof limits missing')
    narrow=report.get('narrowed_claims')
    require(isinstance(narrow,list),'NARROWED CLAIMS must be explicit list (empty means none)')
    if narrow:
        for item in narrow:
            require(isinstance(item,dict) and all(item.get(k) for k in ('decision','reviewer_artifact','strongest_claim','excluded_coverage')), 'narrowed claim lacks reviewed decision/exclusions')
    gates=report.get('gates')
    if not isinstance(gates,list): return errors+['gate roster missing']
    ids=[g.get('id') for g in gates if isinstance(g,dict)]
    require(len(ids)==len(gates) and len(ids)==len(set(ids)) and set(ids)==set(roster()),'binding roster must occur exactly once with no extra IDs')
    byid={g['id']:g for g in gates if isinstance(g,dict) and 'id' in g}
    require(byid.get('F7',{}).get('status')=='NOT PERFORMED','F7 must be NOT PERFORMED')
    for gate in gates:
        if not isinstance(gate,dict): continue
        label=gate.get('id','?')
        require(gate.get('status') in STATUSES,label+': invalid status')
        require(gate.get('claim_class') in CLASSES,label+': invalid claim class')
        require(bool(gate.get('reason')),label+': reason missing')
        require(gate.get('source_commit')==frozen,label+': frozen source mismatch')
        evidence=gate.get('evidence')
        require(isinstance(evidence,list),label+': evidence list missing')
        if gate.get('status')!='NOT PERFORMED':
            require(bool(evidence),label+': attempted gate requires raw evidence')
        if gate.get('status')=='PASSED':
            predicates=gate.get('predicates')
            require(isinstance(predicates,list) and bool(predicates),label+': PASS needs exact gate predicate records')
            if isinstance(predicates,list):
                for predicate in predicates:
                    require(isinstance(predicate,dict) and predicate.get('satisfied') is True and predicate.get('requirement') and predicate.get('evidence_ids'), label+': incomplete PASS predicate')
            require(bool(gate.get('internal_semantic_review')),label+': PASS semantic review absent')
        for record in evidence or []:
            if not isinstance(record,dict): errors.append(label+': invalid evidence record'); continue
            require(record.get('claim_class') in CLASSES,label+': evidence claim class invalid')
            source=record.get('source_commit')
            require(isinstance(source,str) and bool(COMMIT.fullmatch(source)),label+': evidence source commit missing')
            require(source==frozen or (record.get('historical') is True and record.get('non_transfer_reason')),label+': evidence source mismatch without historical non-transfer boundary')
            command=record.get('command',{})
            require(isinstance(command.get('argv'),list) and bool(command.get('argv')) and all(isinstance(v,str) for v in command['argv']),label+': exact argv missing')
            require(command.get('cwd') and isinstance(command.get('environment'),dict),label+': cwd/environment missing')
            require(record.get('started_utc') and record.get('ended_utc'),label+': UTC bounds missing')
            require(isinstance(record.get('result'),dict) and 'exit_code' in record['result'],label+': explicit exit status missing (null remains unknown)')
            require(record.get('tool_versions'),label+': tool versions missing')
            artifacts=record.get('artifacts')
            require(isinstance(artifacts,list) and bool(artifacts),label+': raw artifacts missing')
            for artifact in artifacts or []:
                try:
                    path=(ROOT/artifact['path']).resolve()
                    require(path.is_relative_to(ROOT),label+': artifact outside worktree')
                    require(bool(SHA.fullmatch(artifact.get('sha256',''))),label+': artifact digest missing')
                    require(path.is_file() and digest(path)==artifact.get('sha256'),label+': artifact unavailable/digest mismatch '+str(path))
                except (KeyError,TypeError,OSError) as error:
                    errors.append(label+': unreadable artifact '+str(error))
    for manifest in report.get('regenerated_manifests',[]):
        require(isinstance(manifest,dict),'invalid regenerated manifest')
        if isinstance(manifest,dict) and manifest.get('kind')=='proof' and manifest.get('success') is True:
            require(byid.get('F2',{}).get('status')=='PASSED','positive regenerated proof manifest forbidden without full F2 pass')
            require(manifest.get('successful_run_evidence_id') and manifest.get('source_commit')==frozen,'positive proof manifest lacks same-source successful run')
    return errors

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('report',type=Path)
    args=parser.parse_args()
    try: report=json.loads(args.report.read_text())
    except (OSError,ValueError) as error:
        print('REFUSED: '+str(error));return 1
    if not isinstance(report,dict):
        print('REFUSED: report is not an object'); return 1
    try: errors=inspect(report)
    except Exception as error:
        print('REFUSED: malformed report: '+type(error).__name__+': '+str(error));return 1
    print(json.dumps({'status':'REFUSED' if errors else 'STRUCTURALLY CHECKED','errors':errors,'non_claims':['No semantic gate acceptance','No independent acceptance','No missing outcome inferred as zero']},indent=2))
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())

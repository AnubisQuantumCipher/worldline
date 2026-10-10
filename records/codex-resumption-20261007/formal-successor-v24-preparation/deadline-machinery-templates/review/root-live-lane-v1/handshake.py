"""Root-only ordinary handshake; target argv/runner/scope remain frozen."""
from pathlib import Path
import datetime,json,os,select,subprocess,sys,time,traceback,uuid
sys.dont_write_bytecode=True
from live_check import D,R,sha,save as record,invoke,check_inputs,sample
sys.path.insert(0,str(D))
import authorization
import successor_support
MAIN_DEADLINE = successor_support.inherited_main_deadline()

assert len(sys.argv)==3,'usage: handshake.py MODE EXPECTED_GATE_MANIFEST_SHA256'
mode=sys.argv[1]
os.umask(0o077)
assert mode==authorization.MODE
authorization.check('dispatch')
assert sha(R/'inputs.json')==sys.argv[2],'gate manifest identity mismatch'
gate_manifest=json.loads((R/'inputs.json').read_text())
for rel,digest in gate_manifest['files'].items():assert sha(R/rel)==digest,rel
for path,digest in gate_manifest['external_pins'].items():assert sha(path)==digest,path
# Each invocation has its own immutable receipts; old refusals are never overwritten.
assert '/' not in mode and mode not in ('','.','..'),'invalid mode path'
(R/'attempts'/mode).mkdir(parents=True,exist_ok=True)
out=R/'attempts'/mode/uuid.uuid4().hex
out.mkdir(exist_ok=False)
def save(n,v): record(out,n,v)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
env=dict(os.environ,PATH=json.loads((D/'launch-environment.json').read_text())['PATH'],
         XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')

# Chosen wrapper protocol bounds, separate from unchanged target resource policy.
MAX_CHALLENGES=3
RECEIPT_WAIT_SECONDS=300
RECEIPT_READ_SECONDS=30

def receipt_line(where):
    raw=bytearray()
    deadline=time.monotonic()+RECEIPT_WAIT_SECONDS
    try:
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:
                raise TimeoutError('finite receipt input deadline expired')
            ready,_,_=select.select([sys.stdin.fileno()],[],[],remaining)
            if not ready:
                raise TimeoutError('finite receipt input deadline expired')
            piece=os.read(sys.stdin.fileno(),1)
            if not piece:
                raise EOFError('receipt input closed before complete newline')
            if not raw:
                deadline=time.monotonic()+RECEIPT_READ_SECONDS
            raw.extend(piece)
            if piece==b'\n':
                return bytes(raw).decode('utf-8')
    finally:
        (where/'stdin-response.bin').write_bytes(raw)

def storage(where):
    p=invoke(['/usr/bin/python3','/home/sicarii/.codex/skills/project-vault/scripts/storage_status.py'],
             env,where,'storage-status-command.json')
    value=json.loads(p.stdout)
    record(where,'storage-status.json',value)
    assert value['local_disk_bytes']['free']>value['configured_local_reserve_bytes'],'local reserve unavailable'
    return value

def same_identity(current,previous):
    assert current['units']==previous['units'],'proof lane changed; full preparation required'
    if current['units']:
        for key in ('pid','starttime','cmdline','cgroup','resolved_executable','executed_file_sha256'):
            assert current['process'][key]==previous['process'][key],'proof identity changed; full preparation required'
        assert current['service']['MemoryMax']==previous['service']['MemoryMax']

def exact_receipt(path,parsed,expected):
    receipt=json.loads(path.read_text())
    rows=[json.loads(item['text']) for item in receipt['content'] if item['type']=='text']
    assert any(row['status']=='exact' and row['fields']['parsed']==parsed
               and row['fields']['exact']==expected and row['formal'] is False
               and row['non_claims'] for row in rows),'threshold JACKAL receipt mismatch'
    return receipt

# Derived once through actual MCP JACKAL, never from a stale host-memory sample.
# The complete receipts remain pinned and retain all non-claims.
MIN_MEM_AVAILABLE_KB=16777217
THRESHOLD_PARSED='(8589934592+8589934592)/1024+1'
POSITIVE_BOUNDARY_PARSED='16777217*1024-8589934592-8589934592'
ZERO_BOUNDARY_PARSED='(16777217-1)*1024-8589934592-8589934592'

def threshold_receipts():
    return {
      'minimum_kB':exact_receipt(R/'threshold-receipt.json',THRESHOLD_PARSED,str(MIN_MEM_AVAILABLE_KB)),
      'positive_boundary':exact_receipt(R/'positive-boundary-receipt.json',POSITIVE_BOUNDARY_PARSED,'1024'),
      'previous_boundary':exact_receipt(R/'zero-boundary-receipt.json',ZERO_BOUNDARY_PARSED,'0')}

def meets_fixed_threshold(live):
    # Compare observed integer kB directly; no rounding, tolerance, dynamic credit,
    # arithmetic fallback, old available value or current proof-usage credit.
    return live['MemAvailable_observed_kB']>=MIN_MEM_AVAILABLE_KB

def expression(live):
    # Root still supplies an actual exact receipt for this challenge's observation.
    # Admission of the immediate observation separately uses the pinned threshold.
    return str(live['MemAvailable_observed_kB'])+'*1024-8589934592-8589934592' 

try:
    # All expensive existing root source/tool/vendor/pin checks precede the challenge.
    prepared=out/'preparation';prepared.mkdir()
    pins=check_inputs(prepared,env)
    record(prepared,'fixed-threshold-receipts.json',threshold_receipts())
    proposal_path=D/'reviewed-launch-proposal.json'
    proposal_sha=sha(proposal_path)
    proposal=json.loads(proposal_path.read_text())
    action=next(row for row in proposal['launches'] if row['mode']==mode)
    assert not Path(action['receipt']).exists(),action['receipt']
    prior=[]
    for row in proposal['launches']:
        if row['mode']==mode:break
        result_path=Path(row['receipt'])/'result.json'
        result=json.loads(result_path.read_text())
        assert result['scope_wait']==0 and result['inputs_unchanged'] is True
        assert result['child_wait'] is not None and result['child_wait']['returncode']==0
        prior.append({'mode':row['mode'],'path':str(result_path),'sha256':sha(result_path)})
    record(prepared,'preceding-action-readback.json',prior)
    invoke(['project-vault','pin',str(D)],env,prepared,'active-output-pin.json')
    initial_disk=storage(prepared)
    vault=invoke(['project-vault','status'],env,prepared,'vault-status-command.json')
    (prepared/'vault-status.json').write_text(vault.stdout)
    prepared_live=sample(prepared,env,full_checks=True)
    # Take fresh memory only after every expensive full pin/project/tool pass.
    # No old preflight MemAvailable value or receipt is reused.
    ready=out/'ready';ready.mkdir()
    storage(ready)
    live=sample(ready,env,full_checks=False)
    same_identity(live,prepared_live)
    pre={'action':action,'exact_pins':pins}
    receipt_digests=set()
    for challenge_number in range(1,MAX_CHALLENGES+1):
        challenge_dir=out/('challenge-'+uuid.uuid4().hex);challenge_dir.mkdir()
        challenge={'at':now(),'kind':'ORDINARY_FIXED_CONSERVATIVE_MEMORY_CHALLENGE','mode':mode,
                   'challenge_number':challenge_number,'max_challenges':MAX_CHALLENGES,
                   'receipt_wait_seconds':RECEIPT_WAIT_SECONDS,'receipt_read_seconds':RECEIPT_READ_SECONDS,
                   'proposal_sha256':proposal_sha,'action':action,'preparation':str(prepared),
                   'preparation_live_sample_sha256':sha(prepared/'live-sample.json'),
                   'live_sample':live,'memory_expression':expression(live),
                   'minimum_memavailable_kB':MIN_MEM_AVAILABLE_KB,
                   'threshold_input_manifest_sha256':sys.argv[2],
                   'proof_usage_credit_bytes':0,
                   'immediate_admission':'fresh observed integer kB meets the SAME fixed conservative threshold',
                   'no_target_launch_executed':True,'original_guarantees':'OPEN_UNCHANGED'}
        record(challenge_dir,'challenge.json',challenge)
        challenge_sha=sha(challenge_dir/'challenge.json')
        print(json.dumps({'kind':challenge['kind'],'challenge_path':str(challenge_dir/'challenge.json'),
                          'challenge_sha256':challenge_sha,'memory_expression':challenge['memory_expression'],
                          'reply_fields':['challenge_sha256','receipt_path','receipt_sha256']}),flush=True)
        line=receipt_line(challenge_dir)
        (challenge_dir/'stdin-response.txt').write_text(line)
        assert line,'receipt input closed before admission'
        answer=json.loads(line)
        assert set(answer)=={'challenge_sha256','receipt_path','receipt_sha256'}
        assert answer['challenge_sha256']==challenge_sha,'receipt belongs to another challenge'
        receipt_path=Path(answer['receipt_path']);assert receipt_path.is_absolute()
        receipt_bytes=receipt_path.read_bytes()
        (challenge_dir/'memory-receipt.json').write_bytes(receipt_bytes)
        assert sha(challenge_dir/'memory-receipt.json')==answer['receipt_sha256'],'receipt identity changed'
        assert answer['receipt_sha256'] not in receipt_digests,'previous challenge receipt must not be reused'
        receipt_digests.add(answer['receipt_sha256'])
        receipt=json.loads(receipt_bytes)
        assert any(row['status']=='exact' and row['fields']['parsed']==challenge['memory_expression']
                   and int(row['fields']['exact'])>0 and row['formal'] is False and row['non_claims']
                   for row in [json.loads(item['text']) for item in receipt['content'] if item['type']=='text']), 'required exact positive nonformal JACKAL planning result absent'
        immediate=challenge_dir/'immediate';immediate.mkdir()
        # Cheap controls/action identity first; unchanged target runner still performs
        # complete original source/tool/vendor/environment admission before its child.
        for path,digest in json.loads((R/'control-pins.json').read_text()).items():assert sha(path)==digest,path
        assert sha(proposal_path)==proposal_sha
        current_action=next(row for row in json.loads(proposal_path.read_text())['launches'] if row['mode']==mode)
        assert current_action==action and not Path(action['receipt']).exists()
        for row in prior:assert sha(row['path'])==row['sha256'],row['path']
        disk=storage(immediate)
        assert disk['configured_local_reserve_bytes']==initial_disk['configured_local_reserve_bytes'],'storage reserve policy changed'
        current=sample(immediate,env,full_checks=False)
        same_identity(current,prepared_live)
        # A fresh direct comparison against the independently JACKAL-derived
        # conservative bound replaces monotone snapshot comparison. Neither
        # observed decrease nor proof MemoryCurrent supplies admission credit.
        stale=not meets_fixed_threshold(current)
        if stale:
            record(challenge_dir,'planning-stale.json',{'at':now(),'reason':'fresh memory observation below unchanged conservative minimum',
                'no_target_launch_executed':True,'next_action':('new same-policy challenge, new root JACKAL receipt required'
                    if challenge_number<MAX_CHALLENGES else 'refuse: finite challenge limit exhausted'),
                'no_failed_receipt_reused':True,'original_guarantees':'OPEN_UNCHANGED',
                'observed_memavailable_kB':current['MemAvailable_observed_kB'],
                'minimum_memavailable_kB':MIN_MEM_AVAILABLE_KB})
            if challenge_number==MAX_CHALLENGES:
                raise RuntimeError('finite same-policy memory challenge limit exhausted')
            live=current
            continue
        save('disposition.json',{'at':now(),'mode':mode,'pins':pins,'action':action,
            'challenge_path':str(challenge_dir/'challenge.json'),'challenge_sha256':challenge_sha,
            'memory_receipt_sha256':answer['receipt_sha256'],'planning_status':'exact',
            'planning_parsed':challenge['memory_expression'],
            'planning_is_informational_nonformal_not_future_capacity_guarantee':True,
            'fresh_live_sample':current,'same_lane_identity_and_fixed_conservative_threshold':True,
            'fresh_memavailable_meets_minimum':meets_fixed_threshold(current),
            'minimum_memavailable_kB':MIN_MEM_AVAILABLE_KB,
            'threshold_receipt_sha256':sha(R/'threshold-receipt.json'),
            'positive_boundary_receipt_sha256':sha(R/'positive-boundary-receipt.json'),
            'zero_boundary_receipt_sha256':sha(R/'zero-boundary-receipt.json'),
            'proof_usage_credit_bytes':0,
            'full_pins_checked_before_challenge_not_rehashed_after_receipt':True,
            'unchanged_target_runner_full_admission_before_child_remains_mandatory':True,
            'authority':'ROOT_EXACT_FULL_STRICT_FORMAL_DIAGNOSTIC_ONLY_AFTER_DIFFERENT_AUTHOR_REVIEW',
            'all_original_and_new_proof_native_custody_producer_parent_guarantees':'OPEN_UNCHANGED',
            'no_phase_D1_release_production_acceptance':True})
        break
except BaseException as error:
    save('refusal.json',{'at':now(),'stage':'ordinary_post_preparation_handshake',
        'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc(),
        'no_target_launch_executed':True,'original_guarantees':'OPEN_UNCHANGED'})
    raise

# Original target launcher and all admission checks remain; this owner now waits finitely.
launcher_wait = successor_support.capture_owned(
    pre['action']['launcher_argv'], out, 'launcher', 1000, env=env,
    deadline=MAIN_DEADLINE - 35, hard_deadline=MAIN_DEADLINE,
    term_seconds=25, kill_seconds=5,
    on_started=lambda child: successor_support.retained_owner_record(
        out / 'launcher-start.json', {'at': now(), 'pid': child.pid,
        'argv': pre['action']['launcher_argv'], 'actual_launcher_start_observed': True}))
code = launcher_wait['returncode']
result_path = Path(pre['action']['receipt']) / 'result.json'
try:
    with successor_support.owner_signals(MAIN_DEADLINE):
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        print(json.dumps({'mode': mode, 'launcher_wait': code, 'target_result': result,
                         'owner_control': launcher_wait,
                         'root_disposition_sha256': sha(out / 'disposition.json')}))
        if code:
            print((out / 'launcher.stdout').read_text())
            print((out / 'launcher.stderr').read_text())
except BaseException as error:
    successor_support.retain_terminal_or_refusal(out / 'launcher-display-refusal.json', {
        'actual_launcher_wait': code, 'error': successor_support.owner_error('result_or_display', error),
        'retention_success': False, 'phase_acceptance': False})
    raise
raise SystemExit(successor_support.owner_exit_code(launcher_wait))

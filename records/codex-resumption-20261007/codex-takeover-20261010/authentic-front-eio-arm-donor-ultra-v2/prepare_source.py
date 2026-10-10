"""Source-data-only preparation. Never imports or runs the campaign/injector."""
from pathlib import Path
import ast, difflib, hashlib, json, shutil, stat, subprocess
T=Path(__file__).parent.parent
D=Path(__file__).parent
S=T/'integrated-candidate-v8/source'

def pin(p):
    p=Path(p); b=p.read_bytes(); i=p.lstat(); assert stat.S_ISREG(i.st_mode)
    return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'mode':stat.S_IMODE(i.st_mode)}

def save(name,value):
    p=D/name; p.parent.mkdir(parents=True,exist_ok=True)
    write_exact(p,json.dumps(value,sort_keys=True,ensure_ascii=True,indent=2).encode()+b'\n')
    return pin(p)

def write_exact(path,raw):
    if path.exists():
        assert path.read_bytes()==raw
    else:
        with path.open('xb') as f:f.write(raw)

ARM_DECODER='''def fault_arm(raw, command):
    # This decodes only the native tracer's raw acknowledgment, never a ready flag.
    prefix = b'ACTUAL_SYSCALL_FAULT_ARMED '
    lines = [line for line in raw.splitlines(keepends=True) if line.startswith(prefix)]
    require(len(lines) <= 1, 'CAMPAIGN_DUPLICATE_NATIVE_FAULT_ARM')
    if not lines or not lines[0].endswith(b'\\n'):
        return None
    expected = ('ACTUAL_SYSCALL_FAULT_ARMED pid=' + command[1]
        + ' pidfd=' + command[2] + ' syscall=' + command[3]
        + ' occurrence=' + command[5] + ' effect=' + command[6]
        + ' path_hex=' + os.fsencode(command[4]).hex() + '\\n').encode('ascii')
    require(lines[0] == expected, 'CAMPAIGN_NATIVE_FAULT_ARM_COMMAND_SPLIT')
    return {'raw_line': lines[0].decode('ascii'), 'sha256': sha(lines[0]),
            'selected_command': command}


'''

FAULT='''    async def fault(self, action, armed=None):
        loop = asyncio.get_running_loop()
        deadline = None
        launch_deadline = None
        terminal = None
        child = None
        child_pidfd = None
        target_pidfd = None
        row = None
        out = None
        err = None
        primary = None
        try:
            target = action['target']
            require(target in ('front', 'worker'), 'CAMPAIGN_REAL_FAULT_TARGET_REQUIRED')
            slot = None if target == 'front' else await self.live_slot(action['timeout'])
            pid = os.getpid() if slot is None else slot.owned.worker_host_pid
            injector = action['injector']
            raw = _lease.file(injector, ('DATA',))
            require(sha(raw) == action['injector_sha256'], 'CAMPAIGN_REAL_SYSCALL_INJECTOR_CHANGED')
            path = Path(action['path'])
            root = Path(self.original_descriptor['paths']['authority_root'])
            require(path.is_relative_to(root), 'CAMPAIGN_FAULT_MUST_TARGET_DISPOSABLE_ARTIFACT')
            target_pidfd = os.pidfd_open(pid) if slot is None else os.dup(slot.owned.worker_pidfd)
            command = [injector, str(pid), str(target_pidfd), action['syscall'],
                       str(path), str(action['occurrence']), action['effect']]
            index = len(self.children)
            stdout = self.out / ('fault-' + str(index) + '.stdout')
            stderr = self.out / ('fault-' + str(index) + '.stderr')
            row = {'action': action, 'original_operation': None if slot is None else slot.operation,
                   'argv': command, 'pid': None, 'owner_birth': None, 'owned_pidfd_info': None,
                   'actual_wait': None, 'native_arm': None, 'failure': None,
                   'stdout': str(stdout), 'stderr': str(stderr), 'cleanup': None}
            self.records.append(row)
            out = stdout.open('xb')
            err = stderr.open('xb')
            child = subprocess.Popen(command, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'},
                                     pass_fds=(target_pidfd,), stdout=out, stderr=err)
            self.children.append(child)
            launch_deadline = loop.time() + action['timeout']
            row['pid'] = child.pid
            child_pidfd = os.pidfd_open(child.pid)
            row['owned_pidfd_info'] = Path('/proc/self/fdinfo/' + str(child_pidfd)).read_text()
            require(('\\nPid:\\t' + str(child.pid) + '\\n') in ('\\n' + row['owned_pidfd_info']),
                    'CAMPAIGN_INJECTOR_HELD_PIDFD_PID_CHANGED')
            row['owner_birth'] = _approved.process_facts(child.pid)
            # Original full slot selection precedes this original full child window.
            # No ARM delay renews the terminal timeout or narrows the prior slot timeout.
            deadline = loop.time() + action['timeout']
            if armed is None:
                # Preserve wait:true's direct complete original terminal wait.
                wait = await asyncio.to_thread(child.wait, timeout=action['timeout'])
            else:
                terminal = asyncio.create_task(asyncio.to_thread(child.wait,
                    timeout=action['timeout']))
                while True:
                    native_arm = fault_arm(stderr.read_bytes(), command)
                    if native_arm is not None:
                        row['native_arm'] = native_arm
                        if not armed.done(): armed.set_result(native_arm)
                        break
                    if terminal.done():
                        row['actual_wait'] = await terminal
                        raise RuntimeError('CAMPAIGN_NATIVE_FAULT_ARM_MISSING')
                    require(loop.time() < deadline, 'CAMPAIGN_NATIVE_FAULT_ARM_DEADLINE')
                    await asyncio.sleep(0.001)
                wait = await terminal
            row['actual_wait'] = wait
            actual_stderr = stderr.read_bytes()
            observed_arm = fault_arm(actual_stderr, command)
            require(observed_arm is not None, 'CAMPAIGN_NATIVE_FAULT_ARM_MISSING')
            if row['native_arm'] is None: row['native_arm'] = observed_arm
            require(observed_arm == row['native_arm'],
                    'CAMPAIGN_NATIVE_FAULT_ARM_TERMINAL_SPLIT')
            require(wait == 0 and b'ACTUAL_SYSCALL_FAULT_APPLIED' in actual_stderr,
                    'CAMPAIGN_GENUINE_FILE_IO_OR_CRASH_INJECTION_NOT_EXERCISED')
            return row
        except BaseException as error:
            primary = error
            if row is not None:
                row['failure'] = {'type': type(error).__name__, 'reason': str(error)}
            if armed is not None and not armed.done():
                armed.set_exception(error)
            raise
        finally:
            errors = []
            if child is not None and child.returncode is None:
                cleanup = {'signal': None, 'actual_wait': None, 'failure': None}
                row['cleanup'] = cleanup
                try:
                    # Signal only the actually held injector; never its target/front/worker.
                    require(child_pidfd is not None, 'CAMPAIGN_INJECTOR_CLEANUP_HELD_PIDFD_REQUIRED')
                    actual_return = signal.pidfd_send_signal(child_pidfd, signal.SIGKILL)
                    cleanup['signal'] = {'call': 'pidfd_send_signal', 'pidfd': child_pidfd,
                                         'signal': signal.SIGKILL, 'return': actual_return}
                except ProcessLookupError:
                    cleanup['signal'] = {'call': 'pidfd_send_signal', 'pidfd': child_pidfd,
                                         'signal': signal.SIGKILL, 'error': 'ProcessLookupError'}
                except BaseException as error:
                    errors.append(error)
                try:
                    # Cleanup cannot borrow a fresh timeout or extend the selected action deadline.
                    cleanup['actual_wait'] = await asyncio.to_thread(child.wait,
                        timeout=max(0, (deadline if deadline is not None else launch_deadline) - loop.time()))
                except BaseException as error:
                    cleanup['failure'] = {'type': type(error).__name__, 'reason': str(error)}
                    errors.append(error)
            if terminal is not None:
                if not terminal.done(): terminal.cancel()
                retained_terminal = (await asyncio.gather(terminal, return_exceptions=True))[0]
                row['terminal_task_cleanup'] = (
                    {'type': type(retained_terminal).__name__, 'reason': str(retained_terminal)}
                    if isinstance(retained_terminal, BaseException) else {'actual_wait': retained_terminal})
            for stream, name in ((out, 'stdout'), (err, 'stderr')):
                if stream is not None:
                    try:
                        stream.flush(); os.fsync(stream.fileno()); stream.close()
                        row[name + '_sha256'] = sha(Path(row[name]).read_bytes())
                    except BaseException as error:
                        errors.append(error)
            for fd in (child_pidfd, target_pidfd):
                if fd is not None:
                    try:
                        os.close(fd)
                    except BaseException as error:
                        errors.append(error)
            if errors:
                if primary is None:
                    raise errors[0]
                for error in errors:
                    primary.add_note('Actual injector cleanup/retention failed: ' + repr(error))

'''

C_ARM='''static void armed(pid_t pid, int pidfd, char **argv, unsigned long occurrence) {
    fprintf(stderr, "ACTUAL_SYSCALL_FAULT_ARMED pid=%ld pidfd=%d syscall=%s occurrence=%lu effect=%s path_hex=",
            (long)pid, pidfd, argv[3], occurrence, argv[6]);
    const unsigned char *path = (const unsigned char *)argv[4];
    for (; *path; ++path) fprintf(stderr, "%02x", (unsigned int)*path);
    fputc('\\n', stderr);
    if (fflush(stderr) < 0 || ferror(stderr)) fail("actual arm acknowledgment");
}
'''

def main():
    assert not (D/'AUTHOR-PACKET.json').exists()
    pyrel='protected-root/controls/live_campaign.py'
    crel='protected-root/controls/syscall_fault.c'
    old_py=(S/pyrel).read_text()
    new_py=old_py.replace('import socket\n','import socket\nimport signal\n',1)
    new_py=new_py.replace('class Campaign:\n',ARM_DECODER+'class Campaign:\n',1)
    new_py=new_py.replace('        self.tasks = []\n','        self.tasks = []\n        self.fault_tasks = []\n',1)
    start=new_py.index('    async def fault(self, action):\n')
    end=new_py.index('    def retry(self, action):\n',start)
    new_py=new_py[:start]+FAULT+new_py[end:]
    before="""                if kind in ('client', 'fault'):
                    task = asyncio.create_task(getattr(self, kind)(action))
                    self.tasks.append(task)
                    if action['wait']: await task
"""
    after="""                if kind in ('client', 'fault'):
                    armed = (asyncio.get_running_loop().create_future()
                             if kind == 'fault' and not action['wait'] else None)
                    operation = (self.fault(action, armed) if kind == 'fault'
                                 else self.client(action))
                    task = asyncio.create_task(operation)
                    self.tasks.append(task)
                    if kind == 'fault': self.fault_tasks.append(task)
                    if action['wait']: await task
                    elif armed is not None: await armed
"""
    assert new_py.count(before)==1
    new_py=new_py.replace(before,after)
    before="""            primary = sys.exc_info()[1]
            errors = []
            try:
"""
    after="""            primary = sys.exc_info()[1]
            errors = []
            pending_faults = [task for task in self.fault_tasks if not task.done()]
            for task in pending_faults: task.cancel()
            if pending_faults:
                await asyncio.gather(*pending_faults, return_exceptions=True)
            try:
"""
    assert new_py.count(before)==1
    new_py=new_py.replace(before,after)
    old_c=(S/crel).read_text()
    before='int main(int argc, char **argv) {\n'
    assert old_c.count(before)==1
    new_c=old_c.replace(before,C_ARM+before)
    new_c=new_c.replace('    int pending_signal = 0;\n','    int pending_signal = 0;\n    int arm_emitted = 0;\n',1)
    before='        pending_signal = 0;\n        if (waitpid(pid, &status, __WALL) != pid) fail("actual traced wait");\n'
    after='        pending_signal = 0;\n        if (!arm_emitted) { armed(pid, pidfd, argv, wanted); arm_emitted = 1; }\n        if (waitpid(pid, &status, __WALL) != pid) fail("actual traced wait");\n'
    assert new_c.count(before)==1
    new_c=new_c.replace(before,after)
    changed={pyrel:(old_py,new_py),crel:(old_c,new_c)}
    for rel,(old,new) in changed.items():
        for side,raw in [('preimages',old),('postimages',new)]:
            p=D/side/rel; p.parent.mkdir(parents=True,exist_ok=True)
            write_exact(p,raw.encode())
    forward=''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+r,tofile='b/'+r)) for r,(a,b) in changed.items())
    inverse=''.join(''.join(difflib.unified_diff(b.splitlines(True),a.splitlines(True),fromfile='a/'+r,tofile='b/'+r)) for r,(a,b) in changed.items())
    write_exact(D/'forward.patch',forward.encode())
    write_exact(D/'inverse.patch',inverse.encode())
    before=ast.parse(old_py); after=ast.parse(new_py)
    def methods(tree):
        cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Campaign')
        return {x.name:ast.dump(x,include_attributes=False) for x in cls.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
    bm=methods(before); am=methods(after)
    assert set(bm)==set(am)
    unchanged=[n for n in bm if n not in ('__init__','fault','run')]
    assert all(bm[n]==am[n] for n in unchanged)
    # Preserve the original timeout expressions literally at both phase consumers.
    old_fault=next(x for x in ast.walk(before) if isinstance(x,ast.AsyncFunctionDef) and x.name=='fault')
    new_fault=next(x for x in ast.walk(after) if isinstance(x,ast.AsyncFunctionDef) and x.name=='fault')
    def calls(function,attr):
        return [x for x in ast.walk(function) if isinstance(x,ast.Call)
                and isinstance(x.func,ast.Attribute) and x.func.attr==attr]
    assert ast.dump(calls(old_fault,'live_slot')[0],include_attributes=False)==ast.dump(calls(new_fault,'live_slot')[0],include_attributes=False)
    original_timeout=ast.dump(next(x.value for x in calls(old_fault,'to_thread')[0].keywords if x.arg=='timeout'),include_attributes=False)
    new_timeouts=[ast.dump(next(x.value for x in c.keywords if x.arg=='timeout'),include_attributes=False)
                  for c in calls(new_fault,'to_thread') if c.args and isinstance(c.args[0],ast.Attribute)
                  and c.args[0].attr=='wait']
    assert new_timeouts[0]==original_timeout and new_timeouts[1]==original_timeout
    # The C protocol addition must leave all original selection/effects byte-identical.
    normalized_c=new_c.replace(C_ARM,'',1).replace('    int arm_emitted = 0;\n','',1)
    normalized_c=normalized_c.replace('        if (!arm_emitted) { armed(pid, pidfd, argv, wanted); arm_emitted = 1; }\n','',1)
    assert normalized_c==old_c
    # Decoder-only inert protocol cases: no campaign/native product imports or execution.
    import os
    namespace={'os':os,'require':lambda v,r: v or (_ for _ in ()).throw(RuntimeError(r)),
               'sha':lambda b:hashlib.sha256(b).hexdigest()}
    tree=ast.Module(body=[next(x for x in after.body if isinstance(x,ast.FunctionDef) and x.name=='fault_arm')],type_ignores=[])
    exec(compile(tree,'<inert-native-arm-decoder>','exec'),namespace)
    command=['/unselected/source-only/injector','123','17','fsync','/unselected/bytes-\u03bb','1','eio']
    raw=('ACTUAL_SYSCALL_FAULT_ARMED pid=123 pidfd=17 syscall=fsync occurrence=1 effect=eio path_hex='+os.fsencode(command[4]).hex()+'\n').encode('ascii')
    decoder=namespace['fault_arm']
    assert decoder(raw,command)['raw_line'].encode('ascii')==raw
    assert decoder(raw[:-1],command) is None
    assert decoder(b'FAULT_TARGET_TERMINATED_BEFORE_INJECTION\n',command) is None
    refused={}
    for name,b in [('duplicate',raw+raw),('truncated_duplicate',raw+raw[:-1]),('wrong_target',raw.replace(b'pid=123 ',b'pid=124 ')),
                   ('wrong_pidfd',raw.replace(b'pidfd=17 ',b'pidfd=18 ')),
                   ('wrong_path',raw.replace(b'path_hex=',b'path_hex=00')),
                   ('wrong_syscall',raw.replace(b'syscall=fsync ',b'syscall=openat ')),
                   ('wrong_occurrence',raw.replace(b'occurrence=1 ',b'occurrence=2 ')),
                   ('wrong_effect',raw.replace(b'effect=eio ',b'effect=kill-entry '))]:
        try:decoder(b,command)
        except RuntimeError as error:refused[name]=str(error)
        else:raise AssertionError(name)
    regression=save('INERT-PROTOCOL-REGRESSION.json',{'schema':'worldline.native-fault-arm-inert-source-protocol-regression-v1',
        'complete_source_selected_frame_accepted_by_decoder':True,'truncated_frame_does_not_arm':True,
        'absent_frame_does_not_arm':True,'refusals':refused,'unchanged_campaign_methods':unchanged,
        'original_full_slot_timeout_call_AST_identical':True,
        'original_full_terminal_timeout_expression_AST_identical_for_direct_and_deferred_waits':True,
        'C_original_selection_and_effect_body_byte_identical_after_protocol_addition_removed':True,
        'synthetic_decoder_inputs_only':True,'native_armed_or_applied_outcomes_created':False,'target_execution':False})
    rt=D/'inert-roundtrip'; rt.mkdir(exist_ok=True)
    for rel,(old,new) in changed.items():
        p=rt/rel;p.parent.mkdir(parents=True,exist_ok=True);write_exact(p,old.encode())
    records=[]
    for patch,want in [(D/'forward.patch',1),(D/'inverse.patch',0)]:
        result=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=rt,capture_output=True)
        records.append({'argv':result.args,'actual_returncode':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()})
        assert result.returncode==0
        for rel,versions in changed.items():assert (rt/rel).read_text()==versions[want]
    roundtrip=save('EXACT-ROUNDTRIP.json',{'schema':'worldline.native-fault-arm-source-roundtrip-v1','operations':records,'exact_forward_and_inverse':True,'target_execution':False})
    unchanged_pins={r:pin(S/r) for r in ['protected-root/controls/campaign_registry.py','protected-root/controls/original_client.py',
        'protected-root/controls/assertion_registry.py','protected-root/controls/construction_registry.py',
        'runtime/worldline/protected_root_worker.py','runtime/worldline/root_worker_codec.py','runtime/worldline/custody_mutation_kernel.py']}
    correspondence=save('PRODUCER-CONSUMER-CORRESPONDENCE.json',{'producer':'syscall_fault.c armed() after successful held-target validation/PTRACE_SEIZE/PTRACE_INTERRUPT/initial wait/PTRACE_SYSCALL resume',
        'protocol':'ACTUAL_SYSCALL_FAULT_ARMED pid=PID pidfd=INHERITED_FD syscall=EXACT_NAME occurrence=EXACT_N effect=EXACT_EFFECT path_hex=ACTUAL_ARG_BYTES_HEX\\n',
        'consumer':'live_campaign.fault_arm exact raw complete command-bound line only; absent/truncated is unresolved, mismatch/duplicate refuses',
        'before_starter':'run awaits actual arm future only for fault wait:false; task remains owned and gather retains its later child wait/APPLIED receipt',
        'wait_true':'await original complete fault task and actual child terminal wait; no early return',
        'terminal':'actual child return code zero plus existing raw APPLIED required; arm alone cannot establish applied/coverage/acceptance',
        'deadline':'original live_slot(action.timeout) remains its own complete window before launch/setup; original child.wait(action.timeout) remains the complete terminal window. Deferred ARM and terminal share only that child window; cleanup gets its remaining time, no fresh timeout',
        'cleanup':'actual held injector pidfd only; SIGKILL and actual wait separately retained on failure/cancellation; target/front/worker and original root escrows untouched',
        'failure':'partial raw outputs and ownership row retained before refusal; missing terminal actual_wait remains null, cleanup wait separate; primary error preserved with notes',
        'installation':'authentic installed selected native binary/closure remains future independently authenticated authority; source-only donor provides no compiled or armed/applied result'})
    repair=''.join(''.join(difflib.unified_diff((T/'authentic-front-eio-arm-donor-ultra-v1/postimages'/r).read_text().splitlines(True),b.splitlines(True),
        fromfile='a/'+r,tofile='b/'+r)) for r,(a,b) in changed.items())
    write_exact(D/'v1-to-v2-repair.patch',repair.encode())
    packet={'schema':'worldline.authentic-front-eio-arm-source-author-packet-v2','author':'CodexAuthenticFrontEioArmAuthor',
        'author_agent':'/root/protected_ultra','actual_model_selection':'openai-codex/gpt-6.1-sol:ultra',
        'model_provenance':pin(T/'protected_ultra-actual-launch-provenance.json'),
        'source_context':{'selector':pin(T/'integrated-candidate-v8/source-selection.json'),'independent_source_review':pin(T/'frame-review-draft/integrated-v8-independent-source-review.json')},
        'permitted_names':list(changed),'preimages':{r:pin(D/'preimages'/r) for r in changed},'postimages':{r:pin(D/'postimages'/r) for r in changed},
        'forward_patch':pin(D/'forward.patch'),'inverse_patch':pin(D/'inverse.patch'),'unchanged_original_consumers_and_domains':unchanged_pins,
        'producer_consumer_correspondence':correspondence,'inert_protocol_regression':regression,'exact_roundtrip':roundtrip,
        'preserved_v1':{'packet':pin(T/'authentic-front-eio-arm-donor-ultra-v1/AUTHOR-PACKET.json'),'reason':'original slot then child timeout was incorrectly narrowed by v1; source-only preparation HOLD, never installed/executed'},
        'v1_to_v2_repair_patch':pin(D/'v1-to-v2-repair.patch'),
        'preparer':pin(__file__),'requested_disposition':'QUALIFIED_EXACT_AUTHENTIC_NATIVE_FAULT_ARM_AND_TERMINAL_SOURCE_ONLY',
        'review_destination':str(D/'independent-source-review.json'),'source_only':True,'target_execution':False,
        'actual_armed_or_applied_result':None,'installation':None,'operator_selections':None,'phase_acceptance':False}
    print(json.dumps(save('AUTHOR-PACKET.json',packet)))

if __name__=='__main__':main()

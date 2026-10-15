#!/usr/bin/env python3
"""Prepared ordinary actor-world evidence harness; coordinator runs after review.

Uses actual journals, checkpoint, fork, native kernel and CodexAdapter. It has no
protected principal and no child-world acceptance claim. Output directories are
fresh and retained. No host environment HOME variable is reassigned.
"""
from __future__ import annotations
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import traceback
import signal
import uuid

ROOT = Path(__file__).resolve().parents[2]
OWNED = ROOT / 'scratch/acquisition'
LOCK = Path('/home/sicarii/.worldline-heavy.lock')
ACTOR_ARGS = ('-m', 'gpt-6-luna', '-c', 'model_reasoning_effort=high')
EXPECTED = b'phase1-luna-actor\n'
MISSION = ('Inside this WORLDLINE world, replace state.txt with exactly the UTF-8 text '
           'phase1-luna-actor followed by one newline. Change no other file. '
           'Read no authentication files. Report completion after writing the file.')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, default=str) + '\n')


def cgroup_facts():
    entry = next(line for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
    folder = Path('/sys/fs/cgroup') / entry[3:].lstrip('/')
    return {'path': str(folder), **{key: (folder / key).read_text().strip()
        for key in ('memory.max', 'memory.swap.max', 'memory.peak', 'memory.events')}}


ACTOR_EXECUTABLE_REAL = Path('/home/sicarii/.local/share/mise/installs/codex/0.159.2/bin/codex')
ACTOR_EXECUTABLE_SHA256 = '113aa5d5952a6fd3950a88323219747d0c91978ebee948509a540c8a460e59a3'
ACTOR_COMPANION = Path('/home/sicarii/.local/share/mise/installs/codex/latest/bin/codex-code-mode-host')
ACTOR_COMPANION_REAL = Path('/home/sicarii/.local/share/mise/installs/codex/0.159.2/bin/codex-code-mode-host')
ACTOR_COMPANION_SHA256 = '6979f2fea8cb1d5d72614abfe2f42b16727cdce2c356cc6af933157e732a7277'


def companion_identity():
    if ACTOR_COMPANION.is_symlink() or not ACTOR_COMPANION.is_file() or not os.access(ACTOR_COMPANION, os.X_OK):
        raise RuntimeError('Pinned public Codex companion absent/not regular executable')
    resolved = ACTOR_COMPANION.resolve(strict=True)
    facts = ACTOR_COMPANION.stat()
    value = {'path': str(ACTOR_COMPANION), 'resolved': str(resolved),
             'sha256': sha(ACTOR_COMPANION), 'bytes': facts.st_size,
             'mode': facts.st_mode & 0o7777, 'readonly': True}
    if resolved != ACTOR_COMPANION_REAL or value['sha256'] != ACTOR_COMPANION_SHA256 or value['bytes'] != 66921472 or value['mode'] != 0o755:
        raise RuntimeError('Pinned public Codex companion identity drift')
    return value


def worker_main(args):
    out = args.out.resolve()
    if not out.is_relative_to(OWNED) or args.timeout <= 0:
        raise SystemExit('Fresh output must be under owned scratch and timeout positive')
    out.mkdir(parents=True, exist_ok=False)
    os.chmod(out, 0o700)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / 'runtime'))
    start = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    metadata = {'status': 'UNVERIFIED', 'scope': 'ordinary authentic actor world only',
                'protected_acceptance': 'NOT PERFORMED', 'child_acceptance': 'NOT PERFORMED',
                'independent_acceptance': 'NOT PERFORMED', 'commit': start,
                'argv': sys.argv, 'requested_model_argv': ACTOR_ARGS,
                'reported_model_identity': 'UNVERIFIED until present in actual retained provider output',
                'native_call_observation': 'UNVERIFIED; no profiler installed',
                'aggregate_cap_equivalence': 'NOT CLAIMED; actor service is a sibling cgroup',
                'stage': 'identity', 'writes_root': str(out), 'pid': os.getpid()}
    save(out / 'launch.json', metadata)
    store = None
    world_id = None
    caught = None
    try:
        if start != args.expected_commit:
            raise RuntimeError('Checkout differs from expected frozen commit')
        library = args.library.resolve(strict=True)
        if not library.is_relative_to(ROOT):
            raise RuntimeError('Library must be inside this worktree')
        metadata['library'] = {'path': str(library), 'sha256': sha(library)}
        source_paths = [p for p in (ROOT / 'runtime/worldline').rglob('*.py') if p.is_file()]
        source_paths.extend((ROOT / 'core').glob('*.ads'))
        source_paths.extend((ROOT / 'core').glob('*.adb'))
        metadata['source_hashes'] = {str(p.relative_to(ROOT)): sha(p) for p in sorted(source_paths)}
        (out / 'tracked.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD', '--'], cwd=ROOT))
        if (out / 'tracked.diff').stat().st_size:
            raise RuntimeError('Tracked source changes exist at actor launch')
        metadata['parent_scope'] = cgroup_facts()
        if metadata['parent_scope']['memory.max'] == 'max':
            raise RuntimeError('Run the coordinator-approved heavy scope first; missing MemoryMax')
        memory_cap = int(metadata['parent_scope']['memory.max'])
        expected_cap = int(subprocess.check_output(['numfmt','--from=iec','8G'],text=True))
        if memory_cap != expected_cap or metadata['parent_scope']['memory.swap.max'] != '0':
            raise RuntimeError('Actor harness requires the unchanged 8G, zero-swap outer scope')
        swap_cap = os.sysconf('SC_PAGE_SIZE')
        if not isinstance(swap_cap,int) or swap_cap <= 0:
            raise RuntimeError('Host page size unavailable or invalid')
        metadata['host_page_size_bytes'] = swap_cap
        os.environ['WORLDLINE_CORE_LIB'] = str(library)
        metadata['stage'] = 'core-load'
        from worldline.core import Core
        core = Core(library)
        metadata['core_load'] = 'TESTED actual constructor and ABI checks'
        metadata['stage'] = 'actor-and-credentials'
        from worldline.paths import WorldlinePaths
        from worldline.agents.codex import CodexAdapter
        from worldline.agents.base import AgentContext
        home = out / 'home'
        home.mkdir(mode=0o700)
        (home / '.codex').mkdir(mode=0o700)
        auth_source = Path('/home/sicarii/.codex/auth.json')
        if not auth_source.is_file():
            raise RuntimeError('ADAPTER_AUTH_UNAVAILABLE: existing local auth is absent')
        (home / '.codex/auth.json').symlink_to(auth_source)
        paths = WorldlinePaths(home=home, data=out/'data', state=out/'state', runtime=out/'runtime', config=out/'config')
        paths.ensure()
        found_executable = shutil.which('codex')
        if not found_executable:
            raise RuntimeError('ADAPTER_UNAVAILABLE: real Codex executable missing')
        executable_spelling = Path(found_executable)
        executable = executable_spelling.resolve(strict=True)
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise RuntimeError('ADAPTER_UNAVAILABLE: real Codex executable missing')
        if executable != ACTOR_EXECUTABLE_REAL or sha(executable) != ACTOR_EXECUTABLE_SHA256:
            raise RuntimeError('Pinned original Codex executable identity drift')
        if executable_spelling.with_name('codex-code-mode-host') != ACTOR_COMPANION:
            raise RuntimeError('Codex companion spelling is not the original sibling')
        metadata['actor_companion'] = companion_identity()
        actor = CodexAdapter(str(executable_spelling))
        actor.extra_argv = ACTOR_ARGS
        context = AgentContext(primary_root=out/'work', workspace=out/'work', mission_file=Path('/run/worldline-runtime/mission.txt'),
            world_state=Path('/run/worldline-runtime/world.json'), home=home, is_git_root=False)
        projections = actor.credential_mounts(context)
        if any(item.private_copy for item in projections):
            raise RuntimeError('Credentials must be read-only projections')
        metadata['actor'] = {'executable': str(executable), 'sha256': sha(executable), 'argv': actor.build_argv(context, MISSION),
            'credential_mounts': [{'source': str(item.source), 'target': str(item.target), 'readonly': not item.private_copy} for item in projections]}
        bwrap = shutil.which('bwrap')
        if bwrap is None:
            raise RuntimeError('Read-only Codex version probe requires bwrap')
        version_argv = [bwrap,'--die-with-parent','--unshare-net','--ro-bind','/','/',
                        '--chdir',str(out),'--',str(executable),'--version']
        version_env = {key:os.environ[key] for key in ('PATH','LANG','LC_ALL','TERM') if key in os.environ}
        version = subprocess.run(version_argv,capture_output=True,text=True,timeout=10,
                                 cwd=out,env=version_env)
        save(out/'codex-version.json', {'argv':version_argv,'exit_code':version.returncode,
             'stdout':version.stdout,'stderr':version.stderr,
             'filesystem':'read-only root bind; no writable host home', 'network':'unshared'})
        if version.returncode:
            raise RuntimeError('Read-only Codex version probe failed; no writable fallback')
        metadata['stage'] = 'manager-and-overlay'
        from worldline.linux.systemd import SystemdAdapter
        from worldline.linux.namespaces import BubblewrapSandbox
        systemd = SystemdAdapter()
        metadata['manager'] = systemd.verify_manager()
        metadata['overlay'] = BubblewrapSandbox.capability(paths)
        if metadata['overlay'].get('state') != 'AVAILABLE':
            raise RuntimeError('Actual overlay capability refused')
        if not args.run:
            metadata['status'] = 'TESTED prerequisite probes only; actor NOT PERFORMED'
            return 0
        metadata['stage'] = 'journal-store-provisioning'
        from worldline.config import GlobalConfig
        from worldline.evaluation_pending import PendingJournal, text
        from worldline.evaluation_terminal import TerminalJournal
        from worldline.finalization_journal import FinalizationJournal
        from worldline.store import StateStore
        from worldline.roots import RootManager
        from worldline.linux.inotify import InotifyWatcher
        from worldline.reconcile import PrimeChangeTracker
        from worldline.checkpoint import CheckpointManager
        from worldline.fork import ForkManager
        from worldline.runner import AgentRunner
        from worldline.admission import AdmissionAuthority, Gate, Ledger
        from worldline.model import WorldState
        value = GlobalConfig.default(paths).value
        # Exact production policy parser; admission floors remain the defaults.
        # Swap zero is not accepted by this source's ResourcePolicy parser, so no
        # unsupported zero value is forced into that policy or its unit creation.
        value['readonlyHomePaths'] = [str(executable_spelling), str(ACTOR_COMPANION)]
        value['adapterOptions'] = {'codex': {'argv': list(ACTOR_ARGS)}}
        value['limits']['resources'] = {'memoryMaxBytes':memory_cap,
            'memorySwapMaxBytes':swap_cap, 'timeoutSeconds':args.timeout}
        config = GlobalConfig(paths, value)
        config.save()
        metadata['configuration'] = {'path':str(paths.config_file), 'sha256':sha(paths.config_file),
                                    'resource_policy':config.resource_policy.canonical(),
                                    'ordinary_actor_swap_limit': 'one observed host page; explicit production policy, not inherited',
                                    'aggregate_cap_equivalence':'NOT CLAIMED; sibling service cap is separate'}
        work = out / 'work'
        work.mkdir(mode=0o700)
        (work/'state.txt').write_bytes(b'prime\n')
        (work/'.worldline.json').write_text(json.dumps({'schemaVersion':1,'generated':[],'checks':[],'services':[]})+'\n')
        (out/'mission.txt').write_text(MISSION+'\n')
        with ExitStack() as owned:
            directory = paths.runtime/'ordinary-evaluation'
            directory.mkdir(mode=0o700)
            pending = PendingJournal(directory/'pending-journal.db', directory/'pending-target.db',
                store_id='ordinary-actor:'+str(uuid.uuid4()),library=library,create=True)
            owned.callback(pending.close)
            terminal = TerminalJournal(pending,directory/'terminal-journal.db',directory/'terminal-target.db',library=library,create=True)
            owned.callback(terminal.close)
            finalization = FinalizationJournal(directory/'finalization-journal.db',text(pending.store),library=library,create=True)
            owned.callback(finalization.close)
            store = StateStore(paths,core,evaluation_terminal=terminal,evaluation_finalization=finalization)
            owned.callback(store.close)
            metadata['stage'] = 'production-root-registration'
            roots = RootManager(paths,store,core=core)
            metadata['registration'] = roots.register([work],confirmed=True)
            watched = [(root['root_key'],paths.root_source(root)) for root in store.roots()]
            tracker_holder = {}
            pending_watch_events = []
            watch_lock = threading.Lock()
            def changed(event):
                with watch_lock:
                    if 'tracker' in tracker_holder:
                        tracker_holder['tracker'].external_event(event)
                    else:
                        pending_watch_events.append(event)
            watcher = InotifyWatcher(watched,changed)
            owned.callback(watcher.close)
            tracker = PrimeChangeTracker(store,watcher)
            with watch_lock:
                tracker_holder['tracker'] = tracker
                for event in pending_watch_events:
                    tracker.external_event(event)
            roots.watcher = watcher
            checkpoint = CheckpointManager(paths,store,core=core,watcher=watcher,reconcile=roots.reconcile)
            gate = Gate(AdmissionAuthority(Ledger(paths.runtime),config.admission_floors,
                paths={'data':paths.data,'state':paths.state}),config.resource_policy)
            runner = AgentRunner(paths,store,config,BubblewrapSandbox(paths),systemd,gate,core=core)
            forks = ForkManager(paths,store,config,checkpoint,runner,core=core)
            metadata['stage'] = 'production-checkpoint-and-fork'
            # Actual factory is resolved inside ForkManager; its configured argv
            # carries the mandated model. No manual World/FrozenParent is supplied.
            world = forks.create_world('luna-ordinary',MISSION,'codex')
            world_id = world.instance_id
            metadata['world_id'] = world_id
            unit = systemd.unit_name(world_id)
            metadata['actor_unit'] = unit
            atomic_save(out.parent/'unit-intent.json', {'world_id':world_id, 'unit':unit,
                'source_commit':start,'memory_max_bytes':memory_cap,'memory_swap_max_bytes':swap_cap,
                'policy':config.resource_policy.canonical(),'parent_scope':metadata['parent_scope'],
                'claim':'recorded before forks.run_world; no actor launch yet'})
            approval = wait_file(out.parent/'unit-launch-admission.json')
            if approval.get('admitted') is not True:
                raise RuntimeError('Sibling watcher refused pre-launch ownership handshake')
            save(out/'world-before-run.json',world.record())
            metadata['stage'] = 'production-actor-run'
            with (out/'progress.jsonl').open('x') as progress:
                def update(event,value):
                    progress.write(json.dumps({'event':event,'value':value},default=str)+'\n');progress.flush()
                try:
                    completed = forks.run_world(world,MISSION,progress=update,timeout=args.timeout)
                    save(out/'world-after-run.json',completed.record())
                    metadata['returned_world_state'] = completed.state.value
                    registered = store.roots()
                    target = Path(completed.payload_path)/registered[0]['root_key']/'state.txt'
                    metadata['candidate_state_file'] = {'path':str(target),'exists':target.is_file(),
                        'sha256':sha(target) if target.is_file() else None,
                        'matches_requested_value':target.is_file() and target.read_bytes()==EXPECTED}
                    agent = next((row for row in completed.evidence.get('checks',[]) if row.get('id')=='agent'),None)
                    save(out/'agent-evidence.json',agent)
                    metadata['ordinary_world_outcome_verified'] = (completed.state == WorldState.VALID
                        and metadata['candidate_state_file']['matches_requested_value']
                        and isinstance(agent,dict) and agent.get('exitCode')==0
                        and agent.get('supervision',{}).get('kind')=='SUPERVISED')
                finally:
                    atomic_save(out.parent/'unit-finished.json', {'world_id':world_id,'unit':unit,
                        'stage':metadata['stage'],'claim':'production actor call exited or raised'})
                    settled = wait_file(out.parent/'unit-quiescent.json')
                    metadata['actor_unit_settlement'] = settled
                    if settled.get('quiescent') is not True:
                        raise RuntimeError('Owned actor service quiescence not established')
                    save(out/'jobs.json',store.jobs())
                    if world_id is not None:
                        save(out/'world-retained.json',store.world(world_id).record())
                        save(out/'interruptions.json',finalization.interruptions(world_id))
            metadata['chain_verification'] = store.verify_chains()
            metadata['status'] = ('TESTED ordinary actor world outcome' if metadata.get('ordinary_world_outcome_verified')
                                  else 'FAILED-OPEN ordinary actor world outcome')
        return 0 if metadata.get('ordinary_world_outcome_verified') else 1
    except BaseException as error:
        caught = error
        metadata['status'] = 'FAILED-OPEN authentic attempt or prerequisite'
        metadata['error'] = {'type':type(error).__name__,'code':getattr(error,'code',None),'message':str(error)}
        (out/'traceback.txt').write_text(traceback.format_exc())
        return 1
    finally:
        if world_id is not None and not (out.parent/'unit-finished.json').exists():
            atomic_save(out.parent/'unit-finished.json', {'world_id':world_id,
                'unit':metadata.get('actor_unit'),'stage':metadata['stage'],
                'claim':'worker finalization, including failure before production call'})
        if world_id is not None and (out.parent/'unit-launch-admission.json').exists():
            admission = json.loads((out.parent/'unit-launch-admission.json').read_text())
            if admission.get('admitted') is True:
                metadata['actor_unit_settlement'] = wait_file(out.parent/'unit-quiescent.json')
        metadata['commit_after'] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        metadata['source_unchanged'] = all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in metadata.get('source_hashes',{}).items())
        metadata['library_unchanged'] = ('library' in metadata and Path(metadata['library']['path']).is_file()
                                         and sha(metadata['library']['path'])==metadata['library']['sha256'])
        if 'actor_companion' in metadata:
            try:
                metadata['actor_companion_unchanged'] = companion_identity() == metadata['actor_companion']
            except (OSError, RuntimeError):
                metadata['actor_companion_unchanged'] = False
        identity_changed = (metadata.get('actor_companion_unchanged') is False
                            or metadata['commit_after'] != start or not metadata['source_unchanged']
                            or ('library' in metadata and not metadata['library_unchanged']))
        if identity_changed:
            metadata['status'] = 'FAILED-OPEN source identity changed during attempt'
        # Hash only regular files without following credential symlinks.
        metadata['retained_files'] = {str(p.relative_to(out)):sha(p) for p in out.rglob('*')
            if p.is_file() and not p.is_symlink() and p.name != 'result.json'}
        save(out/'result.json',metadata)
        print(json.dumps({'status':metadata['status'],'stage':metadata['stage'],'out':str(out)},sort_keys=True))
        if identity_changed:
            raise SystemExit(1)


def atomic_save(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.partial-' + uuid.uuid4().hex)
    with temporary.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, default=str)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def record(path, value):
    import datetime
    with Path(path).open('a') as stream:
        stream.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), **value},sort_keys=True)+'\n')
        stream.flush()


def wait_file(path):
    while True:
        try:
            return json.loads(Path(path).read_text())
        except FileNotFoundError:
            time.sleep(0.1)


def command(args, timeout=10):
    try:
        result = subprocess.run(args,capture_output=True,text=True,timeout=timeout)
        return {'argv':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'argv':args,'exit_code':None,'error':type(error).__name__+': '+str(error)}


def properties(result):
    return dict(line.split('=',1) for line in result.get('stdout','').splitlines() if '=' in line)


class OwnUnitWatcher:
    """Own one preannounced UUID unit, never a wildcard or another unit."""
    fields = ('Id','LoadState','ActiveState','SubState','MainPID','InvocationID','ControlGroup',
              'MemoryMax','MemorySwapMax','MemoryPeak','MemorySwapPeak','Result','Restart','KillMode')

    def __init__(self, out, expected_commit, runner=command):
        self.out = out
        self.expected_commit = expected_commit
        self.runner = runner
        self.intent = None
        self.unit = None
        self.admitted = False
        self.manager_root = None
        self.live_cap_observed = False
        self.cap_mismatch = False
        self.last_sample = None
        self.settlement = None
        self.last_stop = None

    def manager_subtree(self):
        result = self.runner(['systemctl','--user','show','--property=ControlGroup','--','-.slice'])
        value = properties(result).get('ControlGroup')
        if result['exit_code'] != 0 or not value or not value.startswith('/'):
            raise RuntimeError('Actual user-manager cgroup subtree unavailable: '+json.dumps(result))
        path = (Path('/sys/fs/cgroup')/value.lstrip('/')).resolve(strict=True)
        if not path.is_relative_to('/sys/fs/cgroup') or path == Path('/sys/fs/cgroup'):
            raise RuntimeError('Invalid user-manager subtree')
        return path, result

    def show(self):
        return self.runner(['systemctl','--user','show',*['--property='+key for key in self.fields],'--',self.unit])

    def matching_groups(self):
        groups = []
        def failed(error):
            raise error
        if not self.manager_root.is_dir():
            raise RuntimeError('User-manager cgroup subtree disappeared')
        for directory, names, _ in os.walk(self.manager_root,followlinks=False,onerror=failed):
            if self.unit in names:
                path = Path(directory)/self.unit
                resolved = path.resolve(strict=True)
                if resolved != path or not resolved.is_relative_to(self.manager_root):
                    raise RuntimeError('Owned cgroup path escaped manager subtree')
                groups.append(path)
        return groups

    def observe(self):
        result = self.show()
        values = properties(result)
        sample = {'unit':self.unit,'manager':result,'properties':values,'groups':[],
                  'quiescent':False,'quiescence_basis':'UNVERIFIED'}
        try:
            paths = self.matching_groups()
            reported = values.get('ControlGroup')
            if reported:
                manager_path = Path('/sys/fs/cgroup')/reported.lstrip('/')
                if manager_path.name != self.unit or not manager_path.is_relative_to(self.manager_root):
                    raise RuntimeError('Manager reported unexpected owned cgroup')
                if manager_path.exists() and manager_path not in paths:
                    raise RuntimeError('Manager cgroup missing from exact-name inventory')
            for path in paths:
                facts = {'path':str(path)}
                for key in ('memory.max','memory.swap.max','memory.peak','memory.current','memory.events','cgroup.events','cgroup.procs'):
                    try:
                        facts[key] = (path/key).read_text().strip()
                    except FileNotFoundError:
                        facts[key] = None
                sample['groups'].append(facts)
            absent = (values.get('LoadState') == 'not-found'
                      and values.get('ActiveState') == 'inactive'
                      and values.get('ControlGroup') == ''
                      and values.get('MainPID') == '0'
                      and result['exit_code'] in (0,1))
            terminal = values.get('ActiveState') in ('inactive','failed') and values.get('MainPID') == '0'
            empty = bool(paths) and all('populated 0' in (row.get('cgroup.events') or '').splitlines()
                                       and row.get('cgroup.procs') == '' for row in sample['groups'])
            if absent and not paths:
                sample['quiescent'] = True
                sample['quiescence_basis'] = 'manager NOT-FOUND and exact UUID cgroup ABSENT in readable user-manager subtree; not a populated-zero measurement'
            elif result['exit_code'] == 0 and terminal and empty:
                sample['quiescent'] = True
                sample['quiescence_basis'] = 'manager terminal/MainPID zero and every matching cgroup measured populated zero with empty cgroup.procs'
            elif result['exit_code'] == 0 and terminal and not paths:
                sample['quiescent'] = True
                sample['quiescence_basis'] = 'manager terminal/MainPID zero and exact UUID cgroup ABSENT in readable user-manager subtree'
            live = result['exit_code'] == 0 and values.get('ActiveState') in ('active','activating')
            if live and self.intent:
                expected = (str(self.intent['memory_max_bytes']),str(self.intent['memory_swap_max_bytes']))
                actual = (values.get('MemoryMax'),values.get('MemorySwapMax'))
                group_caps = [(row.get('memory.max'),row.get('memory.swap.max')) for row in sample['groups']]
                if actual == expected and group_caps and all(caps == expected for caps in group_caps):
                    self.live_cap_observed = True
                    sample['live_cap_observation'] = 'MEASURED matching manager and cgroup memory limits'
                elif (all(item is not None for item in actual) and actual != expected
                      or any(all(item is not None for item in caps) and caps != expected for caps in group_caps)):
                    self.cap_mismatch = True
                    sample['live_cap_observation'] = 'FAILED actual manager or cgroup limits differ'
                else:
                    sample['live_cap_observation'] = 'UNVERIFIED incomplete live measurement'
        except (OSError,RuntimeError) as error:
            sample['observation_error'] = type(error).__name__+': '+str(error)
        self.last_sample = sample
        record(self.out/'unit-observations.jsonl',sample)
        return sample

    def admit(self, intent):
        self.intent = intent
        unit_id = uuid.UUID(intent['world_id'])
        self.unit = 'worldline-'+str(unit_id)+'.service'
        if unit_id.version != 4 or str(unit_id) != intent['world_id'] or intent['unit'] != self.unit:
            raise RuntimeError('Noncanonical own-world UUID unit intent')
        expected_cap = int(subprocess.check_output(['numfmt','--from=iec','8G'],text=True))
        if intent['source_commit'] != self.expected_commit or intent['memory_max_bytes'] != expected_cap:
            raise RuntimeError('Actor source or memory intent mismatch')
        if intent['memory_swap_max_bytes'] != os.sysconf('SC_PAGE_SIZE'):
            raise RuntimeError('Actor swap intent differs from observed one host page')
        self.manager_root, root_receipt = self.manager_subtree()
        record(self.out/'manager-root.jsonl',root_receipt)
        sample = self.observe()
        # A preexisting inactive/failed unit is still not ours. Refuse all except
        # explicit manager absence plus exact-name cgroup absence before launch.
        admitted = (sample['quiescent'] is True
                    and sample['properties'].get('LoadState') == 'not-found'
                    and not sample['groups'])
        self.admitted = admitted
        result = {'admitted':admitted,'unit':self.unit,'world_id':str(unit_id),
                  'prelaunch':sample,'watcher_pid':os.getpid(),
                  'claim':'permission to launch only this fresh unit; actual live limits still UNVERIFIED'}
        atomic_save(self.out/'unit-launch-admission.json',result)
        return admitted

    def stop_once(self):
        if not self.admitted:
            raise RuntimeError('Refusing to stop a unit without fresh ownership admission')
        now = time.monotonic()
        if self.last_stop is None or now-self.last_stop >= 5:
            result = self.runner(['systemctl','--user','stop','--no-block','--',self.unit])
            record(self.out/'unit-stop.jsonl',result)
            self.last_stop = now

    def settle(self):
        if self.settlement is not None:
            return self.settlement
        self.stop_once()
        sample = self.observe()
        if sample['quiescent']:
            self.settlement = {'quiescent':True,'unit':self.unit,'terminal_observation':sample,
                'live_caps_measured':self.live_cap_observed,'cap_mismatch':self.cap_mismatch,
                'qualification':'MEASURED' if self.live_cap_observed and not self.cap_mismatch else 'UNVERIFIED or FAILED live limits',
                'aggregate_cap_equivalence':'NOT CLAIMED; parent and actor have separate cgroups'}
            atomic_save(self.out/'unit-quiescent.json',self.settlement)
        return self.settlement


def base_argv(args, phase, out):
    values = [sys.executable,'-B',str(Path(__file__).resolve()),'--phase',phase,'--out',str(out),
              '--expected-commit',args.expected_commit,'--library',str(args.library.resolve()),
              '--timeout',str(args.timeout),'--scope-timeout',args.scope_timeout]
    if args.run:
        values.append('--run')
    return values


def locked_main(args):
    out = args.out.resolve()
    (out/'scope').mkdir()
    (out/'scope/tmp').mkdir()
    (out/'scope/cache').mkdir()
    watcher = OwnUnitWatcher(out,args.expected_commit)
    cancellation = {'requested':False}
    def cancel(signum, frame):
        cancellation['requested'] = True
        record(out/'signals.jsonl',{'signal':signum,'action':'defer exit until owned units quiescent'})
    for signum in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):
        signal.signal(signum,cancel)
    atomic_save(out/'watcher.json',{'pid':os.getpid(),'source_commit':args.expected_commit,
        'architecture':'lock holder outside capped worker scope; sibling cleanup survives worker OOM',
        'hard_kill_boundary':'External SIGKILL or host failure of this supervisor is not contained by Python; no absolute host-failure guarantee'})
    argv = [sys.executable,'-B',str(ROOT/'scripts/phase1_heavy.py'),'--phase','locked',
            '--timeout',args.scope_timeout,'--swap-max','0','--out',str(out/'scope'),'--',
            *base_argv(args,'worker',out/'worker')]
    atomic_save(out/'worker-launch.json',{'argv':argv,'lock':str(LOCK),
        'claim':'this locked phase is invoked only by outer flock; heavy inner phase deliberately skips recursive flock'})
    process = None
    failure = None
    try:
        with (out/'heavy.stdout').open('xb') as stdout,(out/'heavy.stderr').open('xb') as stderr:
            process = subprocess.Popen(argv,stdout=stdout,stderr=stderr)
            while True:
                if (out/'cancel-request.json').exists():
                    cancellation['requested'] = True
                if watcher.intent is None and (out/'unit-intent.json').exists():
                    try:
                        watcher.admit(json.loads((out/'unit-intent.json').read_text()))
                    except Exception as error:
                        failure = type(error).__name__+': '+str(error)
                        atomic_save(out/'unit-launch-admission.json',{'admitted':False,'error':failure})
                # Only a worker terminal marker/dead scope excludes a future
                # launch after admission. Cancellation first stops its scope.
                ending = (out/'unit-finished.json').exists() or process.poll() is not None
                if watcher.admitted:
                    if ending or watcher.cap_mismatch:
                        watcher.settle()
                    elif watcher.settlement is None:
                        watcher.observe()
                if cancellation['requested']:
                    # Stop only the worker scope created by this attempt, allowing
                    # the existing heavy supervisor to finish its own cleanup.
                    path = out/'scope/scope.jsonl'
                    if path.exists():
                        entry = json.loads(path.read_text().splitlines()[0])
                        scope = entry['unit']
                        import re
                        if not re.fullmatch(r'wl-phase1-[0-9a-f]{32}\.scope',scope):
                            raise RuntimeError('Malformed own scope identity')
                        record(out/'scope-cancel.jsonl',command(['systemctl','--user','stop','--no-block','--',scope]))
                if process.poll() is not None:
                    break
                time.sleep(0.2)
    except BaseException as error:
        failure = type(error).__name__+': '+str(error)
        record(out/'watcher-failure.jsonl',{'error':failure,'traceback':traceback.format_exc()})
    finally:
        # No return/release on unknown service state. Continued failure is retained
        # and leaves this supervisor holding the shared lock for safe own cleanup.
        if watcher.admitted:
            # A supervisor error during the launch handshake must first make the
            # worker unable to launch later. Otherwise an absent-unit ack could
            # race a delayed run_world call and release the lock prematurely.
            while process is not None and process.poll() is None and not (out/'unit-finished.json').exists():
                path = out/'scope/scope.jsonl'
                if path.exists():
                    entry = json.loads(path.read_text().splitlines()[0])
                    scope = entry['unit']
                    import re
                    if re.fullmatch(r'wl-phase1-[0-9a-f]{32}\.scope',scope):
                        record(out/'scope-emergency-stop.jsonl',command(['systemctl','--user','stop','--no-block','--',scope]))
                time.sleep(1)
            while watcher.settlement is None:
                try:
                    watcher.settle()
                except BaseException as error:
                    record(out/'cleanup-errors.jsonl',{'error':type(error).__name__+': '+str(error)})
                if watcher.settlement is None:
                    time.sleep(1)
        if process is not None:
            # Existing heavy supervisor owns and verifies worker-scope cleanup.
            # If it remains live, wait while preserving the global lock.
            while process.poll() is None:
                time.sleep(1)
    code = process.returncode if process is not None else 1
    qualified = (not args.run or watcher.admitted and watcher.settlement is not None
                 and watcher.live_cap_observed and not watcher.cap_mismatch)
    admission_path = out/'scope/admitted.json'
    capacity_refused = (code == 75 and admission_path.exists()
                        and json.loads(admission_path.read_text()) == {'admitted':False})
    if (failure or not qualified or cancellation['requested']) and not capacity_refused:
        code = 1
    atomic_save(out/'locked-result.json',{'exit_code':code,'error':failure,'worker_exit_code':process.returncode if process else None,
        'actor_admitted':watcher.admitted,'actor_settlement':watcher.settlement,'caps_qualified':qualified,
        'native_call_observation':'UNVERIFIED','full_F5':'OPEN','independent_acceptance':'NOT PERFORMED'})
    return code


def outer_main(args):
    out = args.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    os.chmod(out,0o700)
    atomic_save(out/'launch.json',{'argv':sys.argv,'script_sha256':sha(__file__),'lock':str(LOCK),
        'expected_commit':args.expected_commit,'ordinary_subset_only':True,'scope_timeout':args.scope_timeout,
        'aggregate_cap_equivalence':'NOT CLAIMED','worker_memory_max':'8G','worker_memory_swap_max':'0',
        'actor_memory_max':'observed worker cap','actor_memory_swap_max':'observed SC_PAGE_SIZE',
        'actor_timeout_seconds':args.timeout})
    current = {'out':None,'cancelled':False}
    def cancel(signum, frame):
        current['cancelled'] = True
        if current['out'] is not None:
            atomic_save(current['out']/'cancel-request.json',{'signal':signum})
    for signum in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):
        signal.signal(signum,cancel)
    while not current['cancelled']:
        attempt = out/('attempt-'+uuid.uuid4().hex)
        attempt.mkdir()
        current['out'] = attempt
        argv = ['flock',str(LOCK),*base_argv(args,'locked',attempt)]
        record(out/'attempts.jsonl',{'argv':argv,'attempt':str(attempt)})
        code = subprocess.call(argv)
        marker = attempt/'scope/admitted.json'
        admission = json.loads(marker.read_text()) if marker.exists() else None
        if admission == {'admitted':False} and code == 75:
            record(out/'backoff.jsonl',{'reason':'less than required MemAvailable','seconds':300,'lock_released':True})
            deadline = time.monotonic()+300
            while time.monotonic()<deadline and not current['cancelled']:
                time.sleep(1)
            continue
        atomic_save(out/'result.json',{'exit_code':code,'attempt':str(attempt),
            'full_F5':'OPEN','independent_acceptance':'NOT PERFORMED'})
        return code
    atomic_save(out/'result.json',{'exit_code':1,'status':'cancelled with owned cleanup delegated to lock holder'})
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=('outer','locked','worker'),default='outer',help=argparse.SUPPRESS)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--expected-commit',required=True)
    parser.add_argument('--library',required=True,type=Path)
    parser.add_argument('--timeout',required=True,type=int,help='Production actor timeout in seconds')
    parser.add_argument('--scope-timeout',required=True,help='Explicit GNU timeout duration for capped worker')
    parser.add_argument('--run',action='store_true',help='Run actual ordinary Codex actor; omitted means prerequisites only')
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(OWNED) or args.timeout<=0:
        parser.error('Output must be in acquisition scratch and actor timeout positive')
    os.chdir(ROOT)
    runtime = '/run/user/'+str(os.getuid())
    os.environ.setdefault('XDG_RUNTIME_DIR',runtime)
    os.environ.setdefault('DBUS_SESSION_BUS_ADDRESS','unix:path='+runtime+'/bus')
    if args.phase == 'worker':
        return worker_main(args)
    if args.phase == 'locked':
        return locked_main(args)
    return outer_main(args)


if __name__ == '__main__':
    raise SystemExit(main())

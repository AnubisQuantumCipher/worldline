"""Genuine full scoped startup observations without an observation-write effect.

Uses the original actual physical producers and native classify/validate calls.
Unlike _capture's terminal tail, this collector never appends a CLOSED witness
before the native custody startup/recovery action has been decided.
"""
from .protected_startup import require

def capture(resources, *, custody_connection=None, owner_state=None):
    from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    from .protected_resource_runtime import RunObservation
    from .protected_root_supervisor import OwnedRootSupervisor
    from .root_owned_descriptor_roster import capture_root_fact
    from .root_scoped_capture_profile import capture_profile
    require(type(resources) is ProtectedScopedResourcePrincipal,
            'CUSTODY_STARTUP_ACTUAL_COMPLETE_SCOPED_PRODUCER_REQUIRED')
    with resources.gate.mutex, resources.order:
        resources.intact()
        # Capture the existing full history. reconcile_context would append a
        # new scope frame before startup authority had redecided that effect.
        before = resources.current_snapshot()
        current, source, _catalogue = resources._context(before)
        resources.journal.load()
        facts = []; raw = []
        for row in before.rows:
            blank = resources._blank(current.scope, current.resource_epoch, current.universe_head,
                current.ledger_head, row, current.observation_head)
            roster = getattr(resources, 'received_roster', None)
            slot = resources.slots.get(row.bound.reservation.hex())
            if slot is None and roster is not None and roster.has(row):
                physical, physical_source = roster.capture_fact(
                    resources.received_roster_owner, row, blank, current.observation_head.hex())
            elif type(slot) is OwnedRootSupervisor:
                physical, physical_source = capture_root_fact(
                    resources, slot, row, blank, current.observation_head.hex())
            else:
                physical, physical_source = super(ProtectedScopedResourcePrincipal, resources)._facts(
                    row, blank, current.observation_head.hex())
            if row.bound.reservation.hex() not in resources.slots and physical.phase == 'UNAVAILABLE':
                physical, historical = resources._retained_closed(row, physical)
                physical_source['historical'] = historical
            facts.append(physical); raw.append(physical_source)
        facts = tuple(facts)
        initial = tuple(RunObservation(scope=row.scope, resource_epoch=before.state.resource_epoch,
            bound=row.bound, actual_unit=row.actual_unit, cgroup=row.cgroup, invocation=row.invocation,
            observation_head=fact.observation_head, observed='UNKNOWN') for row, fact in zip(before.rows, facts))
        observed = []; decisions = []; classification_material = []
        for row, fact in zip(before.rows, facts):
            material = resources._inspect(before, current, initial, facts,
                resources._request(before, row.bound.reservation))
            native = resources.scoped_kernel.classify(material)
            kind = native.status
            observed.append(RunObservation(scope=row.scope, resource_epoch=before.state.resource_epoch,
                bound=row.bound, actual_unit=fact.actual_unit if kind in ('LIVE','REAPED') else row.actual_unit,
                cgroup=fact.cgroup if kind in ('LIVE','REAPED') else row.cgroup,
                invocation=fact.invocation if kind in ('LIVE','REAPED') else row.invocation,
                observation_head=fact.observation_head, observed=kind))
            decisions.append(native); classification_material.append(material)
        packet = resources._inspect(before, current, tuple(observed), facts)
        observation = resources.scoped_kernel.validate(packet)
        resources.intact()
        complete = capture_profile(resources, packet, tuple(raw), tuple(decisions),
                                   tuple(classification_material), getattr(resources, 'received_roster', None))
        if owner_state is None:
            from .root_worker_current_state import capture_startup_owner_state
            owner_state = capture_startup_owner_state(resources.lease, custody_connection=custody_connection)
        return capture_envelope({
                'material': packet, 'observation': observation,
                'source': resources.lease.source_lease.check(), 'scoped_source': source,
                'physical': tuple(raw), 'classification': tuple(decisions),
                'classification_material': tuple(classification_material),
                'complete_scoped_capture': complete}, owner_state)


def capture_envelope(captured, owner_state):
    """Encode one original observation/provenance/current-owner image."""
    from .root_worker_codec import raw_archive
    profile = (captured['complete_scoped_capture'] if 'complete_scoped_capture' in captured else
               captured['owned_descriptor_roster'])
    captured['owner_state'] = owner_state
    captured['capture'] = raw_archive({'observation': captured['observation'],
        'provenance': profile, 'packet': captured['material'],
        'projection': profile['scoped_projection'], 'owner': owner_state})
    return captured


def admission_identity(info):
    import stat
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode), 'nlink': info.st_nlink,
            'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def _capture_named_source(path, identity_format):
    """Named/no-follow facts, including an actual unavailable read."""
    import os
    import stat
    from pathlib import Path
    path = Path(path)
    observed = {'path': str(path), 'presence': None, 'kind': None, 'identity': None,
                'held_identity': None, 'after_identity': None, 'named_after_identity': None,
                'raw': None, 'link_target': None, 'error': None}
    fd = None
    try:
        info = path.lstat()
        observed['presence'] = 'PRESENT'
        observed['identity'] = identity_format(info)
        if stat.S_ISREG(info.st_mode):
            observed['kind'] = 'REGULAR'
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            observed['held_identity'] = identity_format(os.fstat(fd))
            with os.fdopen(os.dup(fd), 'rb') as stream:
                observed['raw'] = stream.read()
            observed['after_identity'] = identity_format(os.fstat(fd))
            observed['named_after_identity'] = identity_format(path.lstat())
        elif stat.S_ISDIR(info.st_mode):
            observed['kind'] = 'DIRECTORY'
        elif stat.S_ISLNK(info.st_mode):
            observed['kind'] = 'SYMLINK'
            observed['link_target'] = os.readlink(path)
        else:
            observed['kind'] = 'OTHER'
    except OSError as error:
        if isinstance(error, FileNotFoundError) and observed['presence'] is None:
            observed['presence'] = 'ABSENT'
        observed['error'] = {'type': type(error).__name__, 'errno': error.errno, 'message': str(error)}
    finally:
        if fd is not None:
            os.close(fd)
    return observed


def capture_named_source(path):
    return _capture_named_source(path, admission_identity)


def installation_identity(info):
    return {'dev': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid, 'gid': info.st_gid,
            'mode': info.st_mode, 'nlink': info.st_nlink, 'size': info.st_size,
            'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def capture_installation_inventory(spec, source_lease):
    """All actual installed entries; native derives the original manifest."""
    import os
    import shutil
    import sys
    import json
    from pathlib import Path
    from . import protected_startup
    module = sys.modules.get('_worldline_approved_source_loader')
    source = source_lease.check()
    components = {}

    def named(path):
        path = Path(path)
        for parent in (*reversed(path.parents), path if path.is_dir() else path.parent):
            key = str(parent)
            if key not in components:
                components[key] = _capture_named_source(parent, installation_identity)
        return _capture_named_source(path, installation_identity)

    trees = []
    for selector in spec['trees']:
        root = Path(selector)
        observed = named(root)
        entries = []
        tree_error = None
        try:
            for path in sorted(root.rglob('*')):
                entry = named(path)
                entry['relative'] = path.relative_to(root).as_posix()
                entries.append(entry)
        except OSError as error:
            tree_error = {'type': type(error).__name__, 'errno': error.errno, 'message': str(error)}
        trees.append({'selector': selector, 'path': str(root), 'identity': observed['identity'],
                      'kind': observed['kind'], 'error': observed['error'],
                      'link_target': observed['link_target'], 'entries': entries, 'tree_error': tree_error})
    files = []
    for selector in spec['files']:
        entry = named(Path(selector))
        entry['selector'] = selector
        files.append(entry)
    resolutions = {}
    for command in spec['runtime']['tools']:
        found = shutil.which(command)
        resolutions[command] = None if found is None else str(Path(found).resolve(strict=True))
    scoped = None
    if 'resource_scoped_producer' in spec['runtime']:
        path = spec['runtime']['resource_scoped_producer']
        raw = source_lease.file(path, ('DATA',))
        scoped = {'path': path, 'raw': raw, 'config': json.loads(raw)}
    return {'trees': trees, 'files': files, 'components': list(components.values()),
        'interpreter': {'path': os.readlink('/proc/self/exe')},
        'interpreter_flags': {'isolated': sys.flags.isolated, 'no_site': sys.flags.no_site,
                              'dont_write_bytecode': sys.dont_write_bytecode},
        'source_interpreter_flags': source['interpreter_flags'], 'helper': source_lease.helper_path,
        'helper_module': getattr(module, '__file__', None), 'startup_module': protected_startup.__file__,
        'tool_resolutions': resolutions, 'environment_keys': tuple(os.environ),
        'resource_scoped_producer': scoped}


def capture_named_admission_source(path):
    observed = capture_named_source(path)
    observed['named_identity'] = observed['identity']
    if observed['kind'] != 'REGULAR':
        observed['identity'] = None
    return observed


def capture_admission_profiles_from_sources(*, spec, genesis, descriptor_path,
        issuer_state, source_lease, store_initial_snapshot, store_initial_snapshot_raw,
        store_initial_head, initial_envelopes=None):
    """Read both original profiles without constructing a lease or principal.

    The retained initial snapshot is an actual earlier acquisition supplied by
    the real owner. It is not reconstructed from Genesis or current SQL. Native
    admission checks its complete bytes/hash independently of current SQL.
    """
    import sqlite3
    from pathlib import Path
    from .protected_startup import canonical, exact_json, store_snapshot, StartupRefusal
    from .root_worker_codec import scoped_archive
    from .errors import WorldlineError
    source_lease.check()
    root = Path(spec['paths']['authority_root'])
    issuer_state = Path(issuer_state)
    gate_config = capture_named_admission_source(root / 'authority/gate/config.json')
    gate_config_raw = gate_config['raw']
    gate_journal_source = capture_named_admission_source(root / 'authority/gate/state/journal.json')
    issuer_head_source = capture_named_admission_source(issuer_state / 'head.json')

    def json_projection(observed):
        if observed['raw'] is None:
            return None
        try:
            return exact_json(observed['raw'], canonical_required=False)
        except (StartupRefusal, TypeError, ValueError, UnicodeError) as error:
            observed['projection_error'] = {'type': type(error).__name__, 'message': str(error)}
            return None

    gate_journal = json_projection(gate_journal_source)
    anchor = json_projection(issuer_head_source)
    try:
        # Exact original head() projection; no issuer authority grant.
        issuer_head = {'sequence': anchor['sequence'], 'event_head': anchor['event_head'],
                       'head_mac': anchor['mac'], 'authority': 'LOCAL_ROOT_ANCHORED_CAPABILITY_VALUE_ONLY'}
    except (TypeError, KeyError) as error:
        issuer_head_source['projection_error'] = {'type': type(error).__name__, 'message': str(error)}
        issuer_head = None
    issuer_intent = capture_named_admission_source(issuer_state / 'intent.json')
    issuer_temporaries = [capture_named_admission_source(path)
                         for path in sorted(issuer_state.glob('.head-*.tmp'))]
    installation_inventory = capture_installation_inventory(spec, source_lease)
    selected_plan = spec.get('root_worker')
    store_source = capture_named_admission_source(Path(spec['paths']['state']) / 'worldline.sqlite3')
    try:
        snapshot = store_snapshot(Path(store_source['path']))
    except (OSError, sqlite3.Error, StartupRefusal, WorldlineError) as error:
        store_source['projection_error'] = {
            'type': type(error).__name__, 'errno': getattr(error, 'errno', None), 'message': str(error)}
        snapshot = None
    owner_plan_raw = (None if selected_plan is None else
                      capture_named_admission_source(selected_plan['owner_plan'])['raw'])
    snapshot_raw = None if snapshot is None else canonical(snapshot)
    profiles = []
    for name, record in genesis['journals'].items():
        candidate = (record['initial_envelope'] if initial_envelopes is None else
                     initial_envelopes.get(name, record['initial_envelope']))
        try:
            initial_raw = canonical(candidate) + b'\n'
            scoped_archive(candidate)
            initial = candidate
        except (TypeError, ValueError, WorldlineError):
            # No JSON candidate bytes. Native ignores this only when the
            # original admission is already consumed; it is never a fallback
            # to the owner's initial envelope for a nonconsumed request.
            initial = initial_raw = None
        path = Path(record['path'])
        observed_journal = capture_named_admission_source(path)
        parent = capture_named_source(path.parent)
        observed_journal['parent_path'] = str(path.parent)
        observed_journal['parent_identity'] = parent['identity']
        observed_journal['parent_kind'] = parent['kind']
        observed_journal['parent_link_target'] = parent['link_target']
        observed_journal['parent_error'] = parent['error']
        profiles.append({'name': name, 'path': record['path'], 'descriptor_path': str(descriptor_path),
            'initial_envelope': initial, 'initial_envelope_raw': initial_raw,
            'gate_config_raw': gate_config_raw, 'gate_journal': gate_journal,
            'gate_journal_raw': None if gate_journal is None else canonical(gate_journal),
            'issuer_head': issuer_head,
            'issuer_head_raw': None if issuer_head is None else canonical(issuer_head),
            'store_initial_head': store_initial_head,
            'gate_config_source': gate_config, 'gate_journal_source': gate_journal_source,
            'issuer_head_source': issuer_head_source, 'store_source': store_source,
            'store_initial_snapshot': store_initial_snapshot,
            'store_initial_snapshot_raw': store_initial_snapshot_raw,
            'store_snapshot': snapshot, 'store_snapshot_raw': snapshot_raw,
            'observed_journal': observed_journal,
            'issuer_intent': issuer_intent, 'issuer_head_temporaries': issuer_temporaries,
            'installation_inventory': installation_inventory, 'owner_plan_raw': owner_plan_raw})
    source_lease.check()
    return profiles


def capture_original_admission_roster(*, spec, genesis, genesis_raw, descriptor_path,
        descriptor_raw, issuer_state, source_lease, held_fds, store_initial_snapshot,
        store_initial_snapshot_raw, store_initial_head, name, initial_envelope,
        bootstrap_connection=None, head_capture=None):
    """The same original roster from genuine held descriptors, without a lease."""
    import os
    import sqlite3
    from pathlib import Path
    from .protected_startup import StartupRefusal
    from .errors import WorldlineError
    from .root_worker_current_state import _database, _database_connection
    from .root_worker_custody import identity as held_identity

    def scan():
        source = source_lease.check()
        held = [{'path': str(path), 'identity': held_identity(fd),
                 'fdinfo': Path('/proc/self/fdinfo/' + str(fd)).read_bytes()}
                for path, fd in held_fds.items()]
        roster = dict.fromkeys((*spec['provisioned_state'], spec['bootstrap_ledger'],
                                spec['genesis'], str(descriptor_path)))
        paths = []
        for word in roster:
            path = Path(word)
            observed = capture_named_source(path)
            raw = observed['raw']
            entry = {'path': word, 'identity': observed['identity'], 'raw': raw,
                     'kind': observed['kind'], 'presence': observed['presence'],
                     'link_target': observed['link_target'], 'error': observed['error'],
                     'held_identity': observed['held_identity'],
                     'after_identity': observed['after_identity'],
                     'named_after_identity': observed['named_after_identity']}
            if head_capture is not None and os.fsencode(path) == head_capture['path']:
                # The same actual held artifact/SQL observation reaches both
                # native profiles. Keep independent named/raw facts untouched;
                # native source joins determine their correspondence.
                entry['logical_database'] = head_capture['logical_database']
                if head_capture['database_error'] is not None:
                    entry['logical_database_error'] = head_capture['database_error']
            elif type(raw) is bytes and raw.startswith(b'SQLite format 3\x00'):
                try:
                    entry['logical_database'] = (_database_connection(bootstrap_connection)
                        if path == Path(spec['bootstrap_ledger']) and bootstrap_connection is not None
                        else _database(path))
                except (OSError, sqlite3.Error, StartupRefusal, WorldlineError) as error:
                    entry['logical_database'] = None
                    entry['logical_database_error'] = {
                        'type': type(error).__name__, 'message': str(error),
                        'errno': getattr(error, 'errno', None)}
            paths.append(entry)
        return {'installation': spec, 'descriptor_path': str(descriptor_path),
                'descriptor_raw': descriptor_raw, 'source': source,
                'held_locks': held, 'paths': paths}

    before = scan()
    current = scan()
    profiles = capture_admission_profiles_from_sources(
        spec=spec, genesis=genesis, descriptor_path=descriptor_path, issuer_state=issuer_state,
        source_lease=source_lease, store_initial_snapshot=store_initial_snapshot,
        store_initial_snapshot_raw=store_initial_snapshot_raw, store_initial_head=store_initial_head,
        initial_envelopes={name: initial_envelope})
    profile = next(value for value in profiles if value['name'] == name)
    profile['lease_genesis_raw'] = genesis_raw
    profile['lease_genesis'] = genesis
    return {'schema': 'worldline.original-startup-admission-v1',
            'before': before, 'current': current, 'startup_admission': profile}


def capture_original_startup_sources(**sources):
    """Exact native standalone bytes for a real offline or poisoned readback."""
    from .root_worker_codec import scoped_archive
    return scoped_archive(capture_original_admission_roster(**sources))

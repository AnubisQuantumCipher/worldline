"""Export actual original isolated custody commands, never manufacture authority.

The original fixture command arms capture on its genuine V2 journal through
capture(). Main supplies the selected early source lease and real disposable
fixtures. Missing event classes/controls are a hard campaign failure, not skips.
"""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

KINDS = frozenset("""PREPARED HELD RUNNING EXECUTION_NATIVE EXECUTION_ACK HANDOFF_INTENT
FRONT_CLOSE_INTENT FRONT_CLOSED TRANSFER_SENT ROSTER_EVIDENCE CUSTODY_ACK ABANDON
FRONT_RETAINED_ESCROW HANDOFF_ABORT ORIGINAL_PROGRESS ORIGINAL_RESULT HANDLER_TERMINAL
WORKER_RELINQUISH WORKER_REATTACHED CUSTODY_RETURNED CLOSED_NS CLOSED_OUTER CLOSED_RAW
CLOSED_WITNESS PHYSICAL_SETTLED HISTORICAL_SETTLEMENT FRONT_RECONSTRUCTION FRONT_OWNED
UNKNOWN RECONCILED REQUEST_QUEUED REQUEST_TRANSFER_INTENT REQUEST_INTAKE REQUEST_ABANDON
REQUEST_RESPONDED REQUEST_LOST DRAIN_STOP_INTENT DRAIN_FREEZE DRAIN_OFD_EVIDENCE
DRAIN_INTAKE DRAIN_ABANDON DRAIN_RELEASED DRAIN_RECLAIMED""".split())
SCHEMA = 'worldline.custody-original-mutation-controls-v2'
CONTROLS = {'retry', 'cas-stale', 'uncertain', 'full-values',
    'independent-request-operation', 'historical-cleanup', 'carry', 'nullable-inactive'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def durable(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(os.dup(fd), 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(fd)
    directory = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    if Path(path).read_bytes() != raw:
        raise RuntimeError('custody control durable export differs')


class ControlCapture:
    def __init__(self, journal, directory, original_command):
        from worldline.root_worker_journal_v2 import RootCustodyJournalV2
        if type(journal) is not RootCustodyJournalV2 or not original_command:
            raise RuntimeError('actual original custody journal/command required')
        self.journal = journal
        self.directory = Path(directory).resolve(strict=True)
        info = self.directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
            raise RuntimeError('exclusive private isolated control directory required')
        self.original_command = tuple(original_command)
        self.rows = []
        self.operation_native_rows = []
        self.pending = None
        self.staged = {}
        self.producer_source_sha256 = sha(Path(__file__).read_bytes())
        selected = journal.source_lease.check()
        self.selected_source = selected

    def operation_native_call(self,record):
        """Durably retain the real full START/result/exception before guards."""
        from worldline.root_worker_codec import raw_archive
        self.journal.source_lease.check()
        name='operation-native-'+str(len(self.operation_native_rows))+'.archive'
        raw=raw_archive({'record':record,'original_command':self.original_command,
            'producer_source_sha256':self.producer_source_sha256})
        durable(self.directory/name,raw)
        self.operation_native_rows.append({'path':name,'sha256':sha(raw),
            'phase':record['phase'],'name':record['name']})

    def before_effect(self, operation, kind, inputs, decision, before, before_load, context=None):
        """Persist only the actual decision before the target can be killed."""
        self.observe(operation, kind, inputs, decision, before,
                     before_load=before_load, context=context)
        row = self.pending
        self.staged[inputs] = row
        prefix = row['input']['path'].removesuffix('.input.archive')
        durable(self.directory / (prefix + '.native-decision.json'), canonical(self._fragment(row)))

    def _fragment(self, row):
        return {'schema': SCHEMA, 'original_commands': [list(self.original_command)],
                'producer_source_sha256': self.producer_source_sha256, 'cases': [row]}

    def observe(self, operation, kind, inputs, decision, before, after=None,
                before_load=None, after_load=None, error=None, context=None):
        """Record native results from the real consumer without changing them."""
        self.journal.source_lease.check()
        row = self.staged.pop(inputs, None)
        staged = row is not None
        if staged:
            prefix = row['input']['path'].removesuffix('.input.archive')
            if row['expected_status'] != decision.status or row['expected_position'] != decision.position:
                raise RuntimeError('same actual native control decision changed after effects')
        else:
            ordinal = len(self.rows)
            prefix = 'case-' + str(ordinal)
            input_name = prefix + '.input.archive'
            durable(self.directory / input_name, inputs)
            row = {'name': prefix + '-' + kind, 'kind': kind, 'controls': [],
                'input': {'path': input_name, 'sha256': sha(inputs)},
                'expected_status': decision.status, 'expected_position': decision.position,
                'original_command': list(self.original_command),
                'producer_source_sha256': self.producer_source_sha256,
                'operation': operation, 'selected_source': self.selected_source}
            if decision.delta is not None:
                delta = canonical(decision.delta)
                name = prefix + '.delta.json'
                durable(self.directory / name, delta)
                row['delta'] = {'path': name, 'sha256': sha(delta)}
            if context is not None and context['status'] in (0, 1, 2):
                filename = prefix + '.context.json'
                durable(self.directory / filename, context['raw'])
                row['context'] = {'path': filename, 'sha256': sha(context['raw']),
                    'expected_status': context['status'], 'expected_position': context['position']}
        for name, raw, observation in (('before_load', before, before_load),
                                       ('after_load', after, after_load)):
            if raw is not None and observation is not None and name not in row:
                filename = prefix + '.' + name + '.archive'
                durable(self.directory / filename, raw)
                row[name] = {'path': filename, 'sha256': sha(raw),
                    'expected_status': observation.status,
                    'expected_position': observation.position}
        if error is not None:
            row['actual_error'] = {'type': type(error).__name__, 'message': str(error)}
        uncertainty = getattr(self.journal, 'uncertain_append', None)
        if self.journal.poisoned and type(uncertainty) is dict and uncertainty['input'] == inputs:
            filename = prefix + '.uncertainty.archive'
            raw = self.journal.capture_uncertainty()
            durable(self.directory / filename, raw)
            row['uncertainty'] = {'path': filename, 'sha256': sha(raw)}
        if not staged:
            self.rows.append(row)
        else:
            durable(self.directory / (prefix + '.actual-outcome.json'), canonical(self._fragment(row)))
        self.pending = row

    def label(self, *controls):
        """An original control labels only its own actually exercised result."""
        if self.pending is None or not set(controls) <= CONTROLS:
            raise RuntimeError('actual observed control and exact enrolled tag required')
        self.pending['controls'].extend(controls)

    def publish(self):
        manifest = {'schema': SCHEMA,
            'original_commands': [list(self.original_command)],
            'producer_source_sha256': self.producer_source_sha256,
            'cases': self.rows}
        primary=None
        try:durable(self.directory / 'capture.json', canonical(manifest))
        except BaseException as error:primary=error
        try:
            if self.operation_native_rows:
                durable(self.directory/'operation-native-capture.json',canonical({
                    'schema':'worldline.actual-operation-native-call-custody-v1',
                    'original_commands':[list(self.original_command)],
                    'producer_source_sha256':self.producer_source_sha256,
                    'records':self.operation_native_rows,'authority_or_acceptance':False}))
        except BaseException as error:
            if primary is None:primary=error
            else:primary.add_note('actual operation-native publication failure: '+repr(error))
        if primary is not None:raise primary
        return manifest


@contextmanager
def capture(journal, output_directory, original_command):
    if getattr(journal, '_control_capture', None) is not None:
        raise RuntimeError('a real custody journal already has an export owner')
    recorder = ControlCapture(journal, output_directory, original_command)
    journal._control_capture = recorder
    try:
        yield recorder
    finally:
        del journal._control_capture
        recorder.publish()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', required=True)
    parser.add_argument('--library', required=True)
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--captures', required=True, nargs='+')
    parser.add_argument('--kind-roster')
    args = parser.parse_args()
    approved = sys.modules.get('_worldline_approved_source_loader')
    if approved is None:
        raise RuntimeError('the genuine early approved source lease is required')
    source = approved.current()
    source.check()
    if source.file(args.library, (source.files[args.library][0],)) != Path(args.library).read_bytes():
        raise RuntimeError('selected native library bytes differ')
    source.directory_or_absent(args.runtime)
    kinds = KINDS
    if args.kind_roster is not None:
        supplied = json.loads(source.file(args.kind_roster, ('DATA',)))
        if type(supplied) is not list or frozenset(supplied) != KINDS:
            raise RuntimeError('complete native Kind_Name roster differs')
    output = Path(args.export).resolve(strict=True)
    cases = []
    commands = []
    producer_hash = sha(Path(__file__).read_bytes())
    for item in args.captures:
        path = Path(item)
        raw = source.file(str(path), ('DATA',))
        manifest = json.loads(raw)
        if manifest['schema'] != SCHEMA or manifest['producer_source_sha256'] != producer_hash:
            raise RuntimeError('actual original capture source identity differs')
        commands.extend(manifest['original_commands'])
        for row in manifest['cases']:
            name = 'case-' + str(len(cases))
            for slot in ('input', 'delta', 'before_load', 'after_load', 'context', 'uncertainty'):
                if slot not in row:
                    continue
                record = row[slot]
                observed = source.file(str(path.parent / record['path']), ('DATA',))
                if sha(observed) != record['sha256']:
                    raise RuntimeError('complete captured native input/delta bytes differ')
                target = name + '.' + slot
                durable(output / target, observed)
                row[slot] = {**record, 'path': target}
            row['name'] = name + '-' + row['kind']
            cases.append(row)
    positives = {row['kind'] for row in cases if row['expected_status'] == 0 and 'delta' in row
                 and 'context' in row}
    tagged = {tag for row in cases for tag in row['controls']}
    if positives != set(kinds) or not CONTROLS <= tagged:
        raise RuntimeError('full original genuine event/control campaign is incomplete')
    durable(output / 'manifest.json', canonical({'schema': SCHEMA,
        'original_commands': commands, 'producer_source_sha256': producer_hash, 'cases': cases}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Owned lifetime of the selected original composed Ledger service.

Only the actual installed original source may service the existing Ledger RPC.
The service's original configuration, principal checks and SPARK decisions are
unchanged. Readiness is an authenticated actual reply from this owned child;
partial output, exceptions and actual waits remain separately retained.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_SERVICE_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_SERVICE_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import math
import os
from pathlib import Path
import signal
import socket
import stat
import struct
import subprocess
import time


class Lifetime:
    def __init__(self, builder, spec, phase):
        self.builder, self.spec, self.phase = builder, spec, phase
        self.child = self.out = self.err = None
        self.pidfd = None
        self.close_active = self.terminal_resolved = False
        self.record = {'schema':'worldline.original-composed-service-lifetime-v1',
            'phase':phase, 'spec':spec, 'argv':None, 'pid':None, 'start_process':None,
            'ready':None, 'actual_error':None, 'terminal':None,
            'pidfd_acquisition':None, 'pidfd_close':None, 'process_observations':[],
            'readiness_attempts':[], 'terminal_attempts':[],
            'runtime_service_or_native_acceptance':False}
        require = builder.require
        cap = builder.plan['owner_inputs']['original-supervisor']['timeout']
        def finite(value):
            return type(value) is int or (type(value) is float and math.isfinite(value))
        require(type(spec) is dict and set(spec) == {'source','root','early_envelope','environment','timeout'}
                and spec['root'] == 'authority/resource'
                and spec['source'] == str(builder.root/'authority/resource/service.py')
                and finite(spec['timeout']) and spec['timeout'] > 0
                and finite(cap) and cap > 0 and spec['timeout'] == cap
                and type(spec['environment']) is dict
                and all(type(k) is str and type(v) is str for k,v in spec['environment'].items()),
                'FIXTURE_SERVICE_EXACT_ORIGINAL_SELECTED_LIFETIME_REQUIRED')
        self.record['selected_original_supervisor_timeout'] = cap
        self.root = builder.target(spec['root'])
        self.entry_raw = builder.selected(spec['source'], ('SOURCE','ENTRY'))
        self.envelope_raw = builder.selected(spec['early_envelope'], ('DATA',))
        self.prefix = builder.root/('original-resource-service-'+phase)
        self.out_path, self.err_path = Path(str(self.prefix)+'.stdout'), Path(str(self.prefix)+'.stderr')
        self.record['source_sha256'] = builder.sha(self.entry_raw)
        self.record['early_envelope_sha256'] = builder.sha(self.envelope_raw)
        try:
            self.out = self.out_path.open('xb')
            self.err = self.err_path.open('xb')
            command = [_lease.interpreter,'-I','-S','-B',_lease.helper_path,
                '--bootstrap-envelope',spec['early_envelope'],'--entry',spec['source'],
                '--root',str(self.root)]
            self.record['argv'] = command
            self.child = subprocess.Popen(command, cwd=self.root,
                env=dict(spec['environment']), stdout=self.out, stderr=self.err)
            self.record['pid'] = self.child.pid
            builder.closers.append(self.close)
            acquisition = {'pid':self.child.pid, 'fd':None, 'error':None}
            self.record['pidfd_acquisition'] = acquisition
            try:
                self.pidfd = os.pidfd_open(self.child.pid)
                acquisition['fd'] = self.pidfd
            except BaseException as error:
                acquisition['error'] = self.error(error)
                raise
            self.record['start_process'] = self.process()
            deadline = time.monotonic()+spec['timeout']
            while True:
                require(self.child.poll() is None, 'FIXTURE_ORIGINAL_SERVICE_EXITED_BEFORE_READY')
                remaining = deadline-time.monotonic()
                require(remaining > 0, 'FIXTURE_ORIGINAL_SERVICE_READY_TIMEOUT')
                try:
                    ready = self.observe(deadline)
                except (FileNotFoundError,ConnectionRefusedError):
                    time.sleep(min(0.05,remaining))
                    continue
                self.record['ready'] = ready
                break
            self.write('started',self.record)
        except BaseException as error:
            self.record['actual_error'] = self.error(error)
            try:
                self.write('start-failed',self.record)
            except BaseException as retained_error:
                error.add_note('Original service partial start retention failed: '+repr(retained_error))
            if self.child is None:
                for name in ('out','err'):
                    stream = getattr(self,name); setattr(self,name,None)
                    if stream is not None:
                        try:stream.close()
                        except BaseException as close_error:error.add_note('Original service stream close failed: '+repr(close_error))
            raise

    @staticmethod
    def error(error):
        return {'type':type(error).__qualname__,'message':str(error),'args':repr(error.args)}

    def process(self):
        root=Path('/proc')/str(self.child.pid)
        row={'pid':self.child.pid,'stat_hex':None,'starttime':None,
             'status_hex':None,'cgroup_hex':None,'exe_hex':None,'error':None,'state':'PARTIAL'}
        self.record['process_observations'].append(row)
        try:
            raw=(root/'stat').read_bytes();row['stat_hex']=raw.hex()
            suffix=raw[raw.rfind(b')')+2:].split()
            row['starttime']=suffix[19].decode('ascii')
            row['status_hex']=(root/'status').read_bytes().hex()
            row['cgroup_hex']=(root/'cgroup').read_bytes().hex()
            row['exe_hex']=os.fsencode(os.readlink(root/'exe')).hex()
            row['state']='OBSERVED'
            return row
        except BaseException as error:
            row['error']=self.error(error)
            raise

    def observe(self, deadline):
        require=self.builder.require
        def allowance():
            remaining=deadline-time.monotonic()
            require(remaining > 0, 'FIXTURE_ORIGINAL_SERVICE_READY_TIMEOUT')
            return remaining
        path=self.root/'request.sock'
        row={'socket':str(path),'lstat':None,'peer':None,'request_hex':None,
             'request_sent':False,'received_hex':'','response_hex':None,'response':None,
             'actual_process':None,'state':'PARTIAL','error':None}
        self.record['readiness_attempts'].append(row)
        try:
            info=path.lstat()
            row['lstat']={'mode':stat.S_IMODE(info.st_mode),'uid':info.st_uid,
                'gid':info.st_gid,'device':info.st_dev,'inode':info.st_ino}
            require(stat.S_ISSOCK(info.st_mode) and info.st_uid == 0
                    and stat.S_IMODE(info.st_mode) == 0o660,
                    'FIXTURE_ORIGINAL_SERVICE_SOCKET_PROTECTION_REQUIRED')
            with socket.socket(socket.AF_UNIX) as connection:
                connection.settimeout(allowance())
                connection.connect(str(path))
                peer=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
                row['peer']=list(peer)
                require(peer == (self.child.pid,0,0), 'FIXTURE_ORIGINAL_SERVICE_ACTUAL_OWNED_ROOT_PEER_REQUIRED')
                request=self.builder.canonical({'op':'state'})+b'\n'
                row['request_hex']=request.hex()
                connection.settimeout(allowance())
                connection.sendall(request);row['request_sent']=True
                received=bytearray()
                while b'\n' not in received and len(received) < 8_388_609:
                    connection.settimeout(allowance())
                    part=connection.recv(8_388_609-len(received))
                    if not part:break
                    received.extend(part);row['received_hex']=received.hex()
                raw=bytes(received).split(b'\n',1)[0]
                if b'\n' in received:raw+=b'\n'
                row['response_hex']=raw.hex()
                allowance()
                require(raw.endswith(b'\n') and len(raw) <= 8_388_608,
                        'FIXTURE_ORIGINAL_SERVICE_COMPLETE_RAW_REPLY_REQUIRED')
            reply=self.builder.exact(raw);row['response']=reply
            require(set(reply) == {'status','generation','active_reservations'}
                    and reply['status'] == 'OK'
                    and type(reply['generation']) is int and reply['generation'] >= 0
                    and type(reply['active_reservations']) is int and reply['active_reservations'] >= 0,
                    'FIXTURE_ORIGINAL_SERVICE_GENUINE_FULL_STATE_REPLY_REQUIRED')
            current=self.process();row['actual_process']=current
            require(current['starttime'] == self.record['start_process']['starttime']
                    and self.child.poll() is None,
                    'FIXTURE_ORIGINAL_SERVICE_OWNED_PROCESS_CHANGED')
            row['state']='OBSERVED'
            return row
        except BaseException as error:
            row['error']=self.error(error)
            raise

    def write(self, suffix, record):
        path=Path(str(self.prefix)+'.'+suffix+'.json')
        self.builder.create(path,self.builder.canonical(record)+b'\n')
        return {'path':str(path),'sha256':self.builder.sha(path.read_bytes())}

    def send_owned(self, number, terminal, field):
        if self.pidfd is not None:
            signal.pidfd_send_signal(self.pidfd, number)
            terminal['signal_route']='actual-held-pidfd'
        else:
            # Popen returned this actual direct child. A failed pidfd/proc
            # acquisition never discards that unreaped child ownership.
            self.child.send_signal(number)
            terminal['signal_route']='actual-owned-unreaped-Popen'
        terminal[field]=True

    def close(self):
        if self.terminal_resolved or self.close_active:
            return self.record
        self.close_active=True
        primary=sys.exc_info()[1];errors=[]
        terminal={'before':None,'terminate_sent':False,'kill_sent':False,'actual_wait':None,
            'signal_route':None,'state':'UNKNOWN','timed_out':False,'errors':[],
            'stdout':None,'stderr':None}
        self.record['terminal_attempts'].append(terminal)
        self.record['terminal']=terminal
        try:
            if self.child.poll() is None:
                try:
                    terminal['before']=self.process()
                    if self.record['start_process'] is not None:
                        self.builder.require(terminal['before']['starttime'] == self.record['start_process']['starttime'],
                            'FIXTURE_ORIGINAL_SERVICE_CLEANUP_IDENTITY_CHANGED')
                except BaseException as error:errors.append(error)
                try:self.send_owned(signal.SIGTERM,terminal,'terminate_sent')
                except BaseException as error:errors.append(error)
            try:
                terminal['actual_wait']=self.child.wait(timeout=self.spec['timeout'])
            except subprocess.TimeoutExpired as error:
                terminal['timed_out']=True;errors.append(error)
                if self.child.poll() is None:
                    try:self.send_owned(signal.SIGKILL,terminal,'kill_sent')
                    except BaseException as kill_error:errors.append(kill_error)
                terminal['actual_wait']=self.child.wait(timeout=self.spec['timeout'])
            self.terminal_resolved=True
            terminal['state']='OBSERVED'
        except BaseException as error:errors.append(error)
        finally:
            if self.terminal_resolved:
                if self.close in self.builder.closers:self.builder.closers.remove(self.close)
                fd=self.pidfd;self.pidfd=None
                if fd is not None:
                    row={'fd':fd,'closed':False,'error':None};self.record['pidfd_close']=row
                    try:os.close(fd);row['closed']=True
                    except BaseException as error:row['error']=self.error(error);errors.append(error)
            for name in ('out','err'):
                stream=getattr(self,name);setattr(self,name,None)
                if stream is not None:
                    try:stream.flush();os.fsync(stream.fileno())
                    except BaseException as error:errors.append(error)
                    try:stream.close()
                    except BaseException as error:errors.append(error)
            for name,path in (('stdout',self.out_path),('stderr',self.err_path)):
                try:
                    raw=self.builder.protected(path).read_bytes()
                    terminal[name]={'path':str(path),'sha256':self.builder.sha(raw),'bytes':len(raw)}
                except BaseException as error:errors.append(error)
            terminal['errors']=[self.error(error) for error in errors]
            try:self.write('terminal-attempt-'+str(len(self.record['terminal_attempts'])),self.record)
            except BaseException as error:errors.append(error)
            if self.terminal_resolved:
                try:self.write('terminal',self.record)
                except BaseException as error:errors.append(error)
            terminal['errors']=[self.error(error) for error in errors]
            self.close_active=False
        if errors:
            if primary is None:raise errors[0]
            for error in errors:primary.add_note('Original service owned close failed: '+repr(error))
        return self.record


def start(builder, spec, phase):
    return Lifetime(builder,spec,phase)

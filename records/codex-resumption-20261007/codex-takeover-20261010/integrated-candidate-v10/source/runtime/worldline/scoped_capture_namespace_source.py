"""Actual namespace/proc sources for SCM translation, never permission.

This module is source-only in this campaign. No capture is executed on import.
The original root native material and custody fold authenticate the complete
retained original context independently of these factual acquisitions.
"""
from __future__ import annotations

import os
from pathlib import Path

from .protected_startup import require
from .root_worker_custody import identity
from .root_worker_process_capture import RootProcessCapture, _read_at
from .custody_subject_capture import actor_identity


def _namespace(directory, name):
    fd = os.open('ns/' + name, os.O_RDONLY | os.O_CLOEXEC, dir_fd=directory)
    try:
        return {'link': os.readlink('ns/' + name, dir_fd=directory),
                'identity': identity(fd)}
    finally:
        os.close(fd)


def _raw(directory):
    return {name: _read_at(directory, name)
            for name in ('stat', 'status', 'uid_map', 'gid_map')}


def capture_actor_namespace(actor, source):
    """Acquire this actual actor's full proc/maps and namespace identities.

    actor is the original actor_identity snapshot made by the same caller, not
    an asserted remote process. Native parsing joins stable fields independently
    and does not mistake changing CPU/accounting counters for PID identity.
    """
    require(actor['pid'] == os.getpid(), 'SCOPED_NAMESPACE_ACTUAL_SELF_ACTOR_REQUIRED')
    directory = os.open('/proc/self', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        before = _raw(directory)
        namespaces = {name: _namespace(directory, name) for name in ('pid', 'user')}
        after = _raw(directory)
        return {'schema': 'worldline.scoped-actor-namespace-source-v1',
                'actor': actor, 'raw': before, 'after': after,
                'namespaces': namespaces, 'proc_identity': identity(directory),
                'boot': Path('/proc/sys/kernel/random/boot_id').read_bytes(),
                'overflow_uid': Path('/proc/sys/kernel/overflowuid').read_bytes(),
                'overflow_gid': Path('/proc/sys/kernel/overflowgid').read_bytes(),
                'source': source}
    finally:
        os.close(directory)


def _context_frame(owner):
    from .root_worker_closed import ClosedFrontEscrow
    custody = getattr(owner, 'custody', None)
    offer = getattr(owner, 'current_offer', None)
    guard = custody if type(custody) is ClosedFrontEscrow else getattr(owner, 'closed_escrow', None)
    if guard is None:
        guard = getattr(getattr(owner, 'lease', None), 'exec_custody', None)
    if type(guard) is ClosedFrontEscrow:
        require(guard.frame is guard.offer.frame and
                (owner is guard.intake or owner is guard.front or
                 (guard.fresh_lease is owner.lease and
                  getattr(guard, 'fresh_front', None) is owner)),
                'SCOPED_NAMESPACE_ACTUAL_CLOSED_FRONT_ESCROW_REQUIRED')
        return guard.frame, guard.offer.frame['subject_custody']['transfer']
    if custody is not None:
        return custody.frame, custody.subject_intake['transfer']
    if offer is not None:
        return offer.frame, offer.frame['subject_custody']['transfer']
    return None, None


def _root_context(owner, roster, source):
    frame, transfer = _context_frame(owner)
    if frame is None:
        return None
    ack = frame['worker']['execution_ack']
    require(ack is not None, 'SCOPED_NAMESPACE_ORIGINAL_EXECUTION_ACK_REQUIRED')
    execution_event = ack['record']['event']
    execution = execution_event['record']
    operation = frame['operation']
    entries = [entry for entry in roster.frame['rows']
               if entry['kind'] == 'ROOT' and entry['row'].bound.operation.hex() == operation]
    require(len(entries) == 1, 'SCOPED_NAMESPACE_ACTUAL_PRIMARY_ROOT_ROSTER_REQUIRED')
    roles = entries[0]['roles']
    host_proc = roster.fds['host_proc']
    worker_pidfd = roster.fds[roles['worker_pidfd']]
    worker_namespace = roster.fds[roles['worker_namespace']]
    original_process = execution['process']
    process, raw = RootProcessCapture(host_proc, worker_pidfd, worker_namespace,
        owner.source_lease).capture(original_process.actual_unit,
                                   original_process.invocation,
                                   original_process.source_lease)
    return {'original_root_frame': frame, 'current_transfer': transfer,
            'execution_event': execution_event, 'measured': execution['measured'],
            'measured_sender_bytes': bytes.fromhex(execution['measured']['raw_sender_credentials']),
            'original_process': original_process, 'process': process,
            'process_source': raw, 'host_proc_identity': identity(host_proc),
            'worker_pidfd_identity': identity(worker_pidfd),
            'worker_namespace_identity': identity(worker_namespace), 'source': source}


def namespace_source(owner, roster, current_actor=None, *, sender_actor_namespace=None):
    """Acquire the receiver view over actual retained original host-proc FDs.

    A sender's uid_map/gid_map read from a DIFFERENT user namespace describe
    target IDs in the reader's user namespace (Linux proc uid_map grammar).
    Same-user-namespace translation is identity, irrespective of parent maps.
    No PID-zero exemption, transformed credentials or synthetic receipts are
    emitted here: the pure consumer derives every numeric relation.
    """
    source = owner.source_lease.check()
    sender = (roster.frame['sender_actor_namespace'] if sender_actor_namespace is None
              else sender_actor_namespace)
    receiver = capture_actor_namespace(actor_identity() if current_actor is None else current_actor, source)
    sender_ns = sender['namespaces']['pid']['identity']
    receiver_ns = receiver['namespaces']['pid']['identity']
    frame, _transfer = _context_frame(owner)
    held = None if frame is None else frame['origin_descriptors']['worker_namespace']
    sender_is_held = held is not None and (sender_ns['device'], sender_ns['inode']) == (
        held['device'], held['inode'])
    different_pid_namespace = (sender_ns['device'], sender_ns['inode']) != (
        receiver_ns['device'], receiver_ns['inode'])
    context = (_root_context(owner, roster, source)
               if sender_is_held or different_pid_namespace else None)
    if context is not None and (sender_ns['device'], sender_ns['inode']) == (
            context['worker_namespace_identity']['device'],
            context['worker_namespace_identity']['inode']):
        sender_host_pid = context['process'].host_pid
    else:
        sender_host_pid = sender['actor']['pid']
    host_proc = roster.fds['host_proc']
    directory = os.open(str(sender_host_pid), os.O_RDONLY | os.O_DIRECTORY |
                        os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=host_proc)
    try:
        before = _raw(directory)
        namespaces = {name: _namespace(directory, name) for name in ('pid', 'user')}
        after = _raw(directory)
        view = {'raw': before, 'after': after, 'namespaces': namespaces,
                'proc_identity': identity(directory), 'host_proc_identity': identity(host_proc),
                'reader_user_namespace': receiver['namespaces']['user'], 'source': source}
    finally:
        os.close(directory)
    return {'schema': 'worldline.scoped-scm-namespace-source-v1',
            'sender_actor_namespace': sender, 'receiver_actor_namespace': receiver,
            'sender_view': view, 'root_context': context, 'source': source}

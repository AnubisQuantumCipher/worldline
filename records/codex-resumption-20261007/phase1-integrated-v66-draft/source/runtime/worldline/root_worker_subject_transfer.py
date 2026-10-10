"""Complete original custody role roster and post-effect transfer preimages."""
from __future__ import annotations
import os
from .custody_subject_capture import actor_identity,fd_identity,original_roles,role_roster,socket_capture,socket_cookie
from .protected_startup import require

TRAILER='worldline.root-custody-actual-send-transcript-v1'

def role_socket_document(capture):
    return {'schema':'worldline.custody-role-socket-v1','socket':capture}

def offer_descriptors(offer):
    result={'request':offer.original_peer.descriptor()}
    result.update(('lock/'+path,offer.fds[path]) for path in sorted(offer.fds))
    result.update(('origin/'+name,offer.origins[name]) for name in sorted(offer.origins))
    result.update(('scoped/'+name,offer.owned_roster.fds[name]) for name in sorted(offer.owned_roster.fds))
    result.update(('transport/'+name,offer.subject_fds[name]) for name in sorted(offer.subject_fds))
    return result

def received_descriptors(receipt):
    result={'request':receipt.request_fd}
    result.update(('lock/'+path,receipt.fds[path]) for path in sorted(receipt.fds))
    result.update(('origin/'+name,receipt.origins[name]) for name in sorted(receipt.origins))
    result.update(('scoped/'+name,receipt.owned_roster.fds[name]) for name in sorted(receipt.owned_roster.fds))
    result.update(('transport/'+name,receipt.subject_fds[name]) for name in sorted(receipt.subject_fds))
    return result

def prepare_offer(offer):
    source=offer.p.lease.source_lease.check();descriptors=offer_descriptors(offer)
    actor=actor_identity(offer.slot.channel);pidfd=fd_identity(offer.origins['worker_pidfd'])
    locks={'lock/'+path:path for path in offer.fds}
    locks.update(('scoped/'+row['descriptor'],row['path']) for row in offer.owned_roster.frame['lease_locks'])
    for row in getattr(offer.slot.front,'subject_live_roster',()):
        if row['lock_path'] is not None:locks['transport/'+row['role']]=row['lock_path']
    roles=original_roles(descriptors,source,actor,pidfd,locks)
    queued=offer.slot.front.front_queued_requests[offer.slot.operation]
    subject=queued['subject']
    require(subject.owner is offer.slot.front and subject.operation==offer.slot.operation,
        'ROOT_CUSTODY_ACTUAL_ORIGINAL_QUEUED_SUBJECT_REQUIRED')
    subject.root_operation=offer.slot.operation
    original=subject.last_original
    front=socket_capture(offer.original_peer.descriptor(),source)
    cookie,cookie_receipt=socket_cookie(offer.original_peer.descriptor(),source)
    transfer={'mode':'FRESH','frame':None,'sender':actor['credentials'],'received_sender':None,
        'send':None,'receive':None,'roles':role_roster(roles,descriptors,source),'roster':roles,
        'worker_document':None,'origin_user_ns':os.readlink('/proc/self/ns/user'),
        'reader_user_ns':None,'origin_pid_ns':os.readlink('/proc/self/ns/pid'),
        'reader_pid_ns':None,'held_pid_ns':os.readlink('/proc/self/fd/'+str(offer.origins['worker_namespace'])),
        'host_cookie':cookie,'reader_cookie':None,'host_cookie_receipt':cookie_receipt,
        'reader_cookie_receipt':None}
    carrier=socket_capture(offer.slot.channel.fileno(),source)
    transfer.update(send_channel=carrier,send_channel_document=role_socket_document(carrier),
        receive_channel=None,receive_channel_document=None)
    offer.initial_request_subject=subject
    retained=offer.slot.authorize_root()
    native=({'role':'root-admission','material':retained['material'],
        'observation':retained['observation'],'provenance':retained['provenance']},)
    intent=subject.append('REQUEST_TRANSFER_INTENT',original,native=native,
        request=original['original_request'],front_socket=front,transfer=transfer)
    return {'original':original,'front_socket':front,'transfer':transfer,'roles':roles,
        'queued':queued['subject'].journal.require_event(queued['emitter'].intake),'intent':intent}

def _ordered(receipts):
    # Roster collections bind each exact raw syscall to its dynamic role.
    if type(receipts) is dict:
        result=[]
        for name in sorted(receipts):
            value=receipts[name]
            result.extend(value if type(value) in (tuple,list) else (value,))
        return result
    return list(receipts)

def send_trailer(offer):
    return {'schema':TRAILER,'send':list(offer.send_receipts[1:])+_ordered(offer.owned_roster.send_receipts)
            +_ordered(offer.subject_send_receipts),
        'owned_roster_send':offer.owned_roster.send_receipts,'subject_send':offer.subject_send_receipts,
        'roles':offer.frame['subject_custody']['roles']}

def _flags(receipts,name):
    values=[row[name] for row in receipts if name in row]
    if not values:return None
    result=values[0]
    for value in values[1:]:result|=value
    return result

def _stream(receipts,source):
    require(receipts,'ROOT_CUSTODY_COMPLETE_SYSCALL_TRANSCRIPT_REQUIRED')
    return {'fd':receipts[0]['fd'],'frame':b''.join(row['frame'] for row in receipts),
        'rights':b''.join(row['rights'] for row in receipts),
        'parts':[dict(row,raw=row['frame']) for row in receipts],
        'result':sum(row['result'] for row in receipts),'errno':receipts[-1]['errno'],
        'flags':_flags(receipts,'flags'),'input_flags':_flags(receipts,'input_flags'),'source':source}

def capture_received(receipt,trailer,source):
    original=receipt.frame['subject_custody'];roles=original['roles']
    require(type(trailer) is dict and set(trailer)=={'schema','send','owned_roster_send','roles','transfer_event','subject_send'}
        and trailer['schema']==TRAILER and trailer['roles']==roles,'ROOT_CUSTODY_FULL_SEND_TRANSCRIPT_REQUIRED')
    sent=trailer['send'];received=list(receipt.receive_receipts[1:])+_ordered(receipt.owned_roster.receive_receipts)
    received+=_ordered(receipt.subject_receive_receipts)
    require(len(sent)==len(received)==len(roles),'ROOT_CUSTODY_FULL_RIGHTS_TRANSCRIPT_REQUIRED')
    transfer=dict(original['transfer'])
    transfer.update(frame=b''.join(row['frame'] for row in sent),
        received_sender=receipt.sender,send=_stream(sent,sent[0]['source']),
        receive=_stream(received,source),roles=role_roster(roles,received_descriptors(receipt),source,worker_pid=os.getpid()),
        worker_document=receipt.peer.worker_observation(),reader_user_ns=os.readlink('/proc/self/ns/user'),
        reader_pid_ns=os.readlink('/proc/self/ns/pid'))
    cookie,cookie_receipt=socket_cookie(receipt.peer.peer.descriptor(),source)
    transfer.update(reader_cookie=cookie,reader_cookie_receipt=cookie_receipt)
    carrier=socket_capture(receipt.channel.fileno(),source)
    transfer.update(receive_channel=carrier,receive_channel_document=role_socket_document(carrier))
    receipt.subject_intake={'original':original['original'],'front_socket':original['front_socket'],
        'worker_socket':socket_capture(receipt.peer.peer.descriptor(),source),'transfer':transfer}
    receipt.send_transcript=trailer
    receipt.owned_roster.sender_receipts=trailer['owned_roster_send']
    return receipt.subject_intake


def subject_descriptors(front):
    pumps=front.subject_pumps
    if not pumps:return {}
    inventory=front.subject_transport_roster
    result={'inventory/'+name:inventory.fds[name] for name in sorted(inventory.fds)}
    for role,pump in pumps.items():
        result[role]=pump.fd;result[role+'/spool']=pump.spool_fd
    return result



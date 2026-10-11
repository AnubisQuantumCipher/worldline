"""Full live owned-roster SCM synchronization; no copied admission decision."""
from __future__ import annotations
from .custody_subject_capture import actor_identity,socket_capture
from .protected_startup import require
from .root_worker_subject_transfer import role_socket_document


def send_current(service,channel,value,receipts,cause,*,native=None):
    from .root_worker_subject_service import _send_message,_message
    observed=service.native(cause,require_ready=False) if native is None else native
    roster=service.owner._root_capture.owned_roster
    require(not roster.closed,'CUSTODY_SYNC_ACTUAL_LIVE_FULL_ROSTER_REQUIRED')
    source=service.owner.source_lease.check()
    seed={'cause':cause,'material':observed[0]['material'],
          'observation':observed[0]['observation'],'provenance':observed[0]['provenance']}
    header={'frame':roster.frame,'seed':seed,'actor':actor_identity(channel),'source':source}
    actual=dict(value,root_sync=header)
    _send_message(channel,actual,source,receipts)
    roster.send(channel)
    carrier=socket_capture(channel.fileno(),source)
    trailer={'send':dict(roster.send_receipts),'source':source,'actor':actor_identity(channel),
             'channel':carrier,'channel_document':role_socket_document(carrier)}
    _send_message(channel,_message('ROOT_SOURCE_SYNC_TRAILER',transfer=trailer),source,receipts)
    service.source_syncs.append({'header':header,'trailer':trailer,'roster':roster})
    return actual


def receive_current(service,channel,value,raw,sender,receipts):
    from .root_worker_subject_service import _receive_message
    from .root_owned_descriptor_roster import OwnedDescriptorRoster,install_retained_root_refresh
    header=value['root_sync'];source=service.owner.source_lease.check()
    header_receive=receipts[-1]
    roster=OwnedDescriptorRoster.receive(channel,header['frame'],sender,source)
    service.registry_rosters.append(roster)
    packet,trailer_raw,trailer_sender=_receive_message(channel,source,receipts)
    require(packet['kind']=='ROOT_SOURCE_SYNC_TRAILER' and trailer_sender==sender,
            'CUSTODY_SYNC_ACTUAL_SCM_SENDER_CHANGED')
    trailer=packet['transfer']
    roster.sender_receipts=trailer['send']
    carrier=socket_capture(channel.fileno(),source)
    transfer={'header':header,'header_message':value,'header_raw':raw,
              'header_sender':sender,'header_receive':header_receive,
              'send_receipts':trailer['send'],'receive_receipts':dict(roster.receive_receipts),
              'sender_actor':trailer['actor'],'sender_source':trailer['source'],'raw_ucred':sender,
              'send_channel':trailer['channel'],'send_channel_document':trailer['channel_document'],
              'receiver_actor':actor_identity(channel),'receiver_source':source,
              'receive_channel':carrier,'receive_channel_document':role_socket_document(carrier),
              'trailer_message':packet,'trailer_raw':trailer_raw,
              'trailer_sender':trailer_sender,'trailer_receive':receipts[-1]}
    install_retained_root_refresh(service.owner,roster,header['seed'],transfer=transfer)
    service.source_syncs.append({'header':header,'transfer':transfer,'roster':roster})
    return value

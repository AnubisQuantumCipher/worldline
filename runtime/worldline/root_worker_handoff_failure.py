"""Factual failed-handoff capture; the original native mutation decides events.

No transport exception proves an abort, no socket EOF proves ownership, and a
poisoned journal is never retried. All descriptors remain with their real owner.
"""
from .protected_startup import require,private_bytes


def prepare(offer):
    """Retain full actual pre-close inputs before closing any target owner."""
    from .root_worker_custody import CustodyOffer,identity
    from .root_worker_current_state import capture_owner_state
    from .root_worker_root_evidence import scoped_capture
    require(type(offer) is CustodyOffer and offer.state=='PREPARED'
        and not offer.send_receipts,'ROOT_HANDOFF_ACTUAL_UNSENT_OFFER_REQUIRED')
    owner=offer.slot.front;resource=owner.resource_route.resource
    attempts=offer.failure_observations
    row={'source_before':owner.source_lease.check()};attempts.append(row)
    row['owner_before']=capture_owner_state(owner)
    resource.journal.load()
    row['launch_journal_raw']=private_bytes(resource.journal.path)
    row['launch_journal_rows']=dict(resource.journal.rows)
    row['dispatch']=offer.slot.owned.dispatch
    row['held']=offer.slot.owned.held
    require(row['held'] is not None and row['dispatch']['operation']==offer.slot.operation,
        'ROOT_HANDOFF_GENUINE_DISPATCH_HELD_REQUIRED')
    packet,classification,validated,provenance=scoped_capture(resource,offer.slot.owned.row.bound.reservation)
    row['scoped']={'material':packet,'classification':classification,
        'observation':validated,'provenance':provenance}
    row['escrow_origins']={path:identity(fd) for path,fd in offer.fds.items()}
    row['original_peer_origin']=identity(offer.original_peer.descriptor())
    row['source_after']=owner.source_lease.check()
    offer.failure_capture=row


def retain(owned,error,offer):
    """Attempt only original native-produced durable failure transitions.

    The caller retains any failed attempt and then uses the original UNKNOWN
    path. Even a committed event does not close, release, or regrant custody.
    """
    from .protected_root_supervisor import OwnedRootSupervisor
    from .protected_root_worker import RootWorkerSlot
    from .root_worker_custody import CustodyOffer,identity
    from .root_worker_current_state import capture_owner_state
    from .root_worker_root_evidence import append,lock_receipts,native_item,seed
    require(type(owned) is OwnedRootSupervisor,'ROOT_HANDOFF_ACTUAL_SUPERVISOR_REQUIRED')
    if offer is None:return None
    require(type(offer) is CustodyOffer and type(offer.slot) is RootWorkerSlot
        and offer.slot.owned is owned and offer.slot.front is owned.front
        and offer.slot.operation==owned.operation and offer.p is owned.principal,
        'ROOT_HANDOFF_ACTUAL_OWNER_OFFER_JOIN_REQUIRED')
    journal=owned.journal;owner=owned.front
    require(not journal.poisoned,'ROOT_HANDOFF_POISONED_APPEND_CANNOT_RETRY')
    retained=getattr(offer,'failure_capture',None)
    if retained is None:return None
    attempt={'error':{'type':type(error).__qualname__,'module':type(error).__module__,
        'message':str(error),'args':error.args,'errno':getattr(error,'errno',None)},
        'offer_state':offer.state,'source_before':owner.source_lease.check(),
        'send_receipts':tuple(offer.send_receipts),
        'roster_send_receipts':dict(offer.owned_roster.send_receipts),
        'subject_send_receipts':dict(offer.subject_send_receipts)}
    offer.failure_observations.append(attempt)
    # These are real still-held OFDs; no paths are reopened as target owners.
    attempt['owner_current']=capture_owner_state(owner)
    attempt['escrow_current']={path:identity(fd) for path,fd in offer.fds.items()}
    require(set(attempt['escrow_current'])==set(retained['escrow_origins']),
        'ROOT_HANDOFF_FULL_ESCROW_KEYSET_CHANGED')
    attempt['locks']=lock_receipts(owner,attempt['owner_current'],fds=offer.fds)
    transfer=getattr(offer,'transfer_event',None)
    if transfer is not None:
        transfer=journal.require_event(transfer)
        require(transfer['kind']=='TRANSFER_SENT' and transfer['operation']==owned.operation,
            'ROOT_HANDOFF_ACTUAL_TRANSFER_EVENT_REQUIRED')
        attempt['transfer_event']=transfer
        current=attempt['owner_current']
        attempt['abandon_operands']={'transfer_event':transfer['event_id'],
            'locks':attempt['locks'],'seed':seed(owner,current)}
        abandoned=append(owner,owned.operation,'ABANDON',
            {'failure':attempt['error'],'actual_transfer':transfer,'held_escrow':attempt['escrow_current']},
            attempt['abandon_operands'],before=current,current=current)
        attempt['abandon_event']=journal.require_event(abandoned)
        # Recapture after the genuine append. Complete state/native readback,
        # original peer and every retained lock remain factual operands.
        current=capture_owner_state(owner);attempt['owner_after_abandon']=current
        attempt['peer_current']=identity(offer.original_peer.descriptor())
        attempt['escrow_operands']={'abandon_event':abandoned['event_id'],
            'locks':lock_receipts(owner,current,fds=offer.fds),
            'escrow':{'origin':retained['original_peer_origin'],
                'current':attempt['peer_current'],'all_origin':retained['escrow_origins'],
                'all_current':{path:identity(fd) for path,fd in offer.fds.items()}}}
        escrow=append(owner,owned.operation,'FRONT_RETAINED_ESCROW',
            {'failure':attempt['error'],'actual_abandon':abandoned,
                'retained_escrow':attempt['escrow_operands']['escrow']},
            attempt['escrow_operands'],before=current,current=current)
        attempt['escrow_event']=journal.require_event(escrow)
        return attempt['escrow_event']
    # A partial or failed send may have delivered rights. It is not an abort.
    # Native chronology/CAS/alternative ACK checks remain mandatory even here.
    if (offer.send_receipts or offer.owned_roster.send_receipts
        or offer.subject_send_receipts):return None
    captured=retained['scoped'];resource=owner.resource_route.resource
    observed=resource.scoped_kernel.validate(captured['material'])
    attempt['scoped_replay']={'material':captured['material'],'observation':observed,
        'provenance':captured['provenance'],'capture_before_close':retained}
    attempt['abort_operands']={'locks':attempt['locks'],
        'abort':{'launch_journal':{'dispatch':retained['dispatch'],'held':retained['held'],
            'source':retained['source_after'],'raw':retained['launch_journal_raw'],
            'rows':retained['launch_journal_rows']}}}
    aborted=append(owner,owned.operation,'HANDOFF_ABORT',
        {'failure':attempt['error'],'actual_launch':attempt['abort_operands']['abort'],
            'held_escrow':attempt['escrow_current']},attempt['abort_operands'],
        native=(native_item('scoped-validate',captured['material'],observed,captured['provenance']),),
        primitive={'abort_class':'Dispatched'},
        before=attempt['owner_current'],current=attempt['owner_current'])
    attempt['abort_event']=journal.require_event(aborted)
    return attempt['abort_event']

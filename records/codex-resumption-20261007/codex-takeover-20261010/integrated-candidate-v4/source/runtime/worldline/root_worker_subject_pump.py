"""Real descriptor read ownership handoff, not observation escrow intake.

Only explicitly registered subject transports use this route. Original root
supervisor collector drains keep their original owners and closure duties.
"""
from __future__ import annotations
import asyncio,os
from .custody_subject_capture import actor_identity,fd_identity,original_roles,role_roster
from .root_worker_subject_custody import SubjectCustody
from .root_worker_subject_spool import CustodySpool
from .root_worker_codec import raw_archive
from .protected_startup import require

class CustodyDescriptorPump:
    def __init__(self,owner,operation,role,fd,spool_fd,*,root_operation=None,records=None,acquisitions=None):
        self.owner=owner;self.operation=operation;self.role=role;self.fd=fd;self.spool_fd=spool_fd
        self.subject=SubjectCustody(owner,operation,'DESCRIPTOR',role,root_operation=root_operation)
        self.actor=actor_identity();self.source=owner.source_lease.check()
        self.spool=CustodySpool(owner,fd,spool_fd,'read',[] if records is None else records)
        self.task=None;self.stop_requested=False;self.waiting=None;self.finished=False
        self.acquisitions=[] if acquisitions is None else list(acquisitions)
        self.frozen=None;self.ofd=None;self.intake=None;self.released=None
    def start(self):
        require(self.task is None,'ROOT_CUSTODY_DESCRIPTOR_READER_REPLAY')
        os.set_blocking(self.fd,False)
        self.spool.mark(self.actor,True)
        self.task=asyncio.create_task(self._run(),name='worldline-subject-read:'+self.role)
        return self.task
    async def _run(self):
        loop=asyncio.get_running_loop()
        try:
            while not self.stop_requested:
                try:
                    raw,io=self.spool.read(self.actor,65536)
                except BlockingIOError as error:
                    receipt=self.spool.io_receipts[-1]
                    if receipt['result']!=-1 or receipt['errno']!=error.errno:raise
                    self.acquisitions.append(receipt)
                    self.waiting=loop.create_future()
                    def ready():
                        if not self.waiting.done():self.waiting.set_result(None)
                    loop.add_reader(self.fd,ready)
                    try:await self.waiting
                    finally:loop.remove_reader(self.fd);self.waiting=None
                    continue
                self.acquisitions.append(io)
                if not raw:break
                # Yield only after all acquired bytes have actual durable writes.
                await asyncio.sleep(0)
        finally:
            self.spool.mark(self.actor,False)
            self.finished=True
    async def freeze(self,live_roster):
        require(self.task is not None and self.frozen is None,'ROOT_CUSTODY_ACTUAL_DRAIN_INTERVAL_REQUIRED')
        if self.finished:
            # Start an actual new owned acquisition interval, then stop it
            # before scheduling another read. EOF never stands for FREEZE.
            self.task=None;self.finished=False;self.stop_requested=False
            self.actor=actor_identity();self.start()
        descriptor={'role':self.role,'fd':self.fd,'identity':fd_identity(self.fd),'roster':live_roster}
        original={'live_roster':live_roster,'descriptor':descriptor,'acquisitions':list(self.acquisitions)}
        # The STOP witness is the complete actual OPEN interval. There is no
        # acquisition after setting stop_requested; an already acquired chunk
        # completes its real pwrite/fsync before the task observes that flag.
        stop=self.subject.drain_stop(original,descriptor,self.spool.snapshot())
        self.stop_requested=True
        if self.waiting is not None and not self.waiting.done():self.waiting.set_result(None)
        await self.task
        original={'live_roster':live_roster,'descriptor':descriptor,'stop_event':stop,
            'acquisitions':list(self.acquisitions)}
        spool=self.spool.snapshot()
        frozen=self.subject.drain_freeze(original,descriptor,spool)
        self.frozen={'event':frozen,'original':original,'descriptor':descriptor,'spool':spool,
            'records':list(self.spool.records),'operation':self.operation,'root_operation':self.subject.root_operation}
        return self.frozen
    def ofd_evidence(self,transfer,worker_report):
        require(self.frozen is not None,'ROOT_CUSTODY_DRAIN_FREEZE_REQUIRED')
        original=dict(self.frozen['original'],worker_report=worker_report)
        ofd={'send':transfer['send'],'worker_report':raw_archive(worker_report),
            'worker_report_source':worker_report['source'],'worker_report_actor':worker_report['actor'],
            'worker_report_native_observations':raw_archive(worker_report['native_observations']),
            'roles':transfer['roles'],'kcmp':[row['kcmp'] for row in transfer['roles']],
            'locks':[row['flock'] for row in transfer['roles']]}
        event=self.subject.drain_ofd_evidence(original,self.frozen['descriptor'],transfer,ofd)
        self.ofd={'event':event,'original':original,'descriptor':self.frozen['descriptor'],'ofd':ofd}
        return self.ofd
    def release(self):
        require(self.ofd is not None and self.released is None,'ROOT_CUSTODY_DRAIN_OFD_EVIDENCE_REQUIRED')
        events=[event for event in self.owner.custody_journal.history(self.operation)
            if event['subject_kind']=='DESCRIPTOR' and event['subject']==self.role and event['kind']=='DRAIN_INTAKE']
        require(len(events)==1,'ROOT_CUSTODY_GENUINE_DRAIN_INTAKE_REQUIRED')
        self.owner.custody_journal.require_event(events[0])
        self.released=self.subject.drain_release(self.ofd['original'],self.ofd['descriptor'])
        self.fd=None
        return self.released

def register_reader(owner,operation,role,fd,spool_fd,*,root_operation=None):
    pumps=owner.subject_pumps
    require(role not in pumps,'ROOT_CUSTODY_DESCRIPTOR_ROLE_REPLAY')
    pump=CustodyDescriptorPump(owner,operation,role,fd,spool_fd,root_operation=root_operation)
    pumps[role]=pump;pump.start()
    return pump

async def freeze_readers(front,root_operation):
    pumps=front.subject_pumps
    if not pumps:return {}
    from .protected_root_worker import RootWorkerSlot
    slot=front.slots.get(root_operation)
    require(type(slot) is RootWorkerSlot and slot.front is front,'ROOT_CUSTODY_ACTUAL_ROOT_SLOT_REQUIRED')
    offer=front.current_offer
    require(offer.slot is slot,'ROOT_CUSTODY_ACTUAL_RETAINED_OFFER_REQUIRED')
    inventory=front._retained_owned_roster
    inventory.intact(front);inventory.escrow=True
    front.subject_transport_roster=inventory
    # A complete caller-owned actual roster, including every present subject
    # reader and spool. Roles are dynamic, never restricted to stdout/stderr.
    descriptors={'inventory/'+name:inventory.fds[name] for name in sorted(inventory.fds)}
    for role,pump in pumps.items():
        require(pump.owner is front and pump.fd is not None,'ROOT_CUSTODY_ACTUAL_READER_OWNER_REQUIRED')
        require(role not in descriptors and role+'/spool' not in descriptors,
            'ROOT_CUSTODY_DESCRIPTOR_ROLE_ALIAS')
        descriptors[role]=pump.fd;descriptors[role+'/spool']=pump.spool_fd
    source=front.source_lease.check();actor=actor_identity()
    pidfd=fd_identity(slot.owned.worker_pidfd)
    locks={'inventory/'+row['descriptor']:row['path'] for row in inventory.frame['lease_locks']}
    roster=original_roles({name:descriptors[name] for name in sorted(descriptors)},source,actor,pidfd,locks)
    front.subject_live_roster=roster
    for pump in pumps.values():await pump.freeze(roster)
    return {role:pump.frozen for role,pump in pumps.items()}


"""Complete actual read/write interval custody, independent of pipe EOF.

The caller retains this whole transcript in each original descriptor event.
Native fold derives Position and whether the interval is open or closed.
"""
from __future__ import annotations
import hashlib,os
from .custody_subject_capture import fd_identity
from .protected_startup import require

class CustodySpool:
    def __init__(self,owner,descriptor_fd,spool_fd,direction,records):
        require(direction in ('read','write') and type(records) is list,
            'ROOT_CUSTODY_COMPLETE_SPOOL_HISTORY_REQUIRED')
        self.owner=owner;self.descriptor_fd=descriptor_fd;self.fd=spool_fd
        self.direction=direction;self.records=records
        self.source=owner.source_lease.check();self.descriptor_identity=fd_identity(descriptor_fd)
        self.position=sum(len(row['data']) for row in records if row['kind']=='CHUNK')
        self.sync_receipts=[]
        self.io_receipts=[];self.write_receipts=[];self.readback_receipts=[];self.pending=None
    def _sync(self):
        receipt={'call':'fsync','fd':self.fd,'args':{'fd':self.fd},
            'source':self.owner.source_lease.check()}
        self.sync_receipts.append(receipt)
        try:os.fsync(self.fd)
        except OSError as error:
            receipt.update(result=-1,errno=error.errno)
            error.custody_spool_receipt=receipt
            raise
        receipt.update(result=0,errno=0)
        return receipt
    def mark(self,actor,armed):
        kind=('WRITE_ARMED' if armed else 'W_DONE') if self.direction=='write' else ('ARMED' if armed else 'DISARMED')
        row={'kind':kind,'owner':actor,'position':self.position,'length':0,'data':b'',
            'sha256':hashlib.sha256(b'').hexdigest(),'spool_fd':self.fd,
            'descriptor_fd':self.descriptor_fd,'source':self.source,'write':None,'io':None,'fsync':self._sync()}
        self.records.append(row)
        return row
    def read(self,actor,maximum):
        require(self.direction=='read','ROOT_CUSTODY_READ_SPOOL_REQUIRED')
        io={'call':'read','fd':self.descriptor_fd,'args':{'fd':self.descriptor_fd,'maximum':maximum},
            'identity':fd_identity(self.descriptor_fd),'source':self.owner.source_lease.check()}
        self.io_receipts.append(io)
        try:raw=os.read(self.descriptor_fd,maximum)
        except OSError as error:
            io.update(raw=None,result=-1,errno=error.errno)
            error.custody_io_receipt=io
            raise
        io.update(raw=raw,result=len(raw),errno=0)
        return self._retain(actor,raw,io)
    def write(self,actor,raw):
        require(self.direction=='write' and type(raw) is bytes,'ROOT_CUSTODY_WRITE_SPOOL_REQUIRED')
        # A partial write records only bytes actually written. It is not W_DONE.
        io={'call':'write','fd':self.descriptor_fd,'args':{'fd':self.descriptor_fd,'data':raw},
            'identity':fd_identity(self.descriptor_fd),'source':self.owner.source_lease.check()}
        self.io_receipts.append(io)
        try:count=os.write(self.descriptor_fd,raw)
        except OSError as error:
            io.update(raw=None,result=-1,errno=error.errno)
            error.custody_io_receipt=io
            raise
        actual=raw[:count];io.update(raw=actual,result=count,errno=0)
        return self._retain(actor,actual,io)
    def _retain(self,actor,raw,io):
        position=self.position;remaining=raw;receipts=[]
        if not raw:return raw,io
        self.pending={'owner':actor,'position':position,'data':raw,'io':io,'writes':receipts}
        while remaining:
            offset=position+len(raw)-len(remaining)
            receipt={'call':'pwrite','fd':self.fd,'offset':offset,'data':remaining,
                'args':{'fd':self.fd,'offset':offset,'data':remaining},
                'source':self.owner.source_lease.check()}
            receipts.append(receipt);self.write_receipts.append(receipt)
            try:count=os.pwrite(self.fd,remaining,offset)
            except OSError as error:
                receipt.update(result=-1,errno=error.errno)
                error.custody_spool_receipt=receipt
                raise
            receipt.update(result=count,errno=0)
            require(count>0,'ROOT_CUSTODY_SPOOL_WRITE_UNKNOWN')
            remaining=remaining[count:]
        # The original whole descriptor IO is never sliced into fabricated IO.
        # Native rejoins every actual partial pwrite and the one original IO.
        write=receipts[0] if len(receipts)==1 else {
            'call':'pwrite-stream','fd':self.fd,'offset':position,'data':raw,
            'result':len(raw),'errno':0,'source':self.source,'parts':receipts}
        if len(receipts)==1:write=dict(write,parts=None)
        row={'kind':'CHUNK','owner':actor,'position':position,'length':len(raw),
            'data':raw,'sha256':hashlib.sha256(raw).hexdigest(),'spool_fd':self.fd,
            'descriptor_fd':self.descriptor_fd,'source':self.source,'write':write,'io':io,'fsync':self._sync()}
        self.records.append(row);self.position+=len(raw);self.pending=None
        return raw,io
    def snapshot(self):
        sync=self._sync();before=fd_identity(self.fd);raw=[];position=0
        while True:
            receipt={'call':'pread','fd':self.fd,'offset':position,
                'args':{'fd':self.fd,'maximum':65536,'offset':position},
                'source':self.owner.source_lease.check()}
            self.readback_receipts.append(receipt)
            try:piece=os.pread(self.fd,65536,position)
            except OSError as error:
                receipt.update(raw=None,result=-1,errno=error.errno)
                error.custody_spool_receipt=receipt
                raise
            receipt.update(raw=piece,result=len(piece),errno=0)
            if not piece:break
            raw.append(piece);position+=len(piece)
        after=fd_identity(self.fd)
        require(before==after,'ROOT_CUSTODY_SPOOL_READBACK_CHANGED')
        return {'direction':self.direction,'records':list(self.records),'raw':b''.join(raw),
            'fd':self.fd,'identity':after,'fsync':sync,'position':self.position,
            'descriptor_identity':self.descriptor_identity,'io_receipts':list(self.io_receipts),
            'write_receipts':list(self.write_receipts),'readback_receipts':list(self.readback_receipts),
            'sync_receipts':list(self.sync_receipts),'pending':self.pending}

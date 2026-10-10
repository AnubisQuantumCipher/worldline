"""Lossless owner conjunction data. No instance of this class is authority."""
from dataclasses import dataclass
from .evaluation_history import EvaluationCursor
from .evaluation_authority import owner_projection, selected_owner_projection
from .owner_retry_audit import RetryAudit, FullScope, decide_retry, authorize_retry_collapse, authorize_checkpoint
from .errors import WorldlineError

@dataclass(frozen=True)
class OwnerCollapseData:
    mode: str
    scope: FullScope
    world: object
    requirement: str | None
    before_material: object
    after_material: object
    request: object
    receipt: object
    current_epoch: int | None
    prepared: object
    resulting: bytes | None
    event: str | None

    def retry_projection(self,core):
        before=owner_projection(None,self.world,self.requirement,core=core,material=self.before_material)
        after=owner_projection(None,self.world,self.requirement,core=core,material=self.after_material)
        cursor=after.current if self.prepared is None else EvaluationCursor(self.prepared['epoch'],self.prepared['run'])
        audit=RetryAudit(self.request,self.receipt,after.current,cursor,self.current_epoch)
        reason=decide_retry(before.records,after.records,before.finalization,after.finalization,audit,core=core)
        if reason!='READY':raise WorldlineError('OWNER_RETRY_'+reason,'complete native retry audit refused packet data')
        return before,after,audit
    def selected(self,core):
        _before,after,_audit=self.retry_projection(core)
        return selected_owner_projection(self.world,after)
    def decide(self,core,values):
        if self.mode=='RETRY_EVALUATION':
            before,after,audit=self.retry_projection(core)
            return authorize_retry_collapse(before.records,after.records,before.finalization,after.finalization,audit,values,self.scope,core=core)
        if self.mode=='ADOPT_REQUIREMENT':
            projection=owner_projection(None,self.world,self.requirement,core=core,material=self.before_material)
            return authorize_checkpoint(projection.records,projection.finalization,values,self.resulting,self.scope,self.request,core=core)
        if self.mode=='CHECKPOINT_EQUAL':
            return authorize_checkpoint((),None,values,self.resulting,self.scope,None,core=core)
        raise WorldlineError('OWNER_COLLAPSE_MODE_INVALID','owner conjunction data mode differs')

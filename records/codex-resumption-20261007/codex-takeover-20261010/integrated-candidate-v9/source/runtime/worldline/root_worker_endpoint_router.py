"""One public endpoint routed to the actual live or reconstructed owner.

Follow-up requests during a detached root use its separately measured custody
channel and independently reserved operation. Closed front semantic owners are
never consulted. Only the original full CLOSED collector installs a new front.
"""
import asyncio
from .protected_startup import require

class RootEndpointRouter:
    def __init__(self,front,daemon):
        from .protected_root_worker import RootWorkerFront
        from .daemon import WorldlineDaemon
        require(type(front) is RootWorkerFront and type(daemon) is WorldlineDaemon
            and daemon.store is front.principal.store,'ROOT_ROUTER_REAL_ORIGINAL_ENDPOINT_REQUIRED')
        self.front,self.daemon=front,daemon;self.lock=asyncio.Lock();daemon._protected_root_router=self
    async def dispatch_redirect(self,caller,line,writer):
        async with self.lock:
            front=self.front
            if front.phase!='FRONT_OWNED':
                if front.phase=='WORKER_OWNED':
                    from .root_worker_custody import CustodyOffer
                    offer=front.current_offer
                    require(type(offer) is CustodyOffer and offer.slot.front is front,
                        'ROOT_ROUTER_ACTUAL_LIVE_CUSTODY_OFFER_REQUIRED')
                    front.custody_journal.require_event(offer.ack_event)
                    service=offer.subject_service
                    require(service.owner is front and service.offer is offer,
                        'ROOT_ROUTER_ACTUAL_LIVE_SUBJECT_SERVICE_REQUIRED')
                    await service.dispatch_line(caller,line,writer)
                    return True
                tasks=tuple(front.collectors.values())
                require(tasks,'ROOT_ROUTER_NO_AUTHENTIC_CLOSED_COLLECTOR')
                await asyncio.gather(*tasks)
                require(front.phase=='RECONSTRUCTED_CLOSED' and getattr(front,'fresh_front',None) is not None,
                        'ROOT_ROUTER_FULL_FRESH_RECONSTRUCTION_NOT_COMMITTED')
                fresh=front.fresh_front
                require(fresh.prior_owner is front and fresh.phase=='FRONT_OWNED',
                        'ROOT_ROUTER_FRESH_OWNERSHIP_LINEAGE_CHANGED')
                self.front,self.daemon=fresh,fresh.daemon;self.daemon._protected_root_router=self
            selected=self.daemon
        if caller is selected:return False
        await selected._dispatch_line(line,writer);return True
    async def publish_after_invoke(self,caller):
        # Worker publication completed before its authenticated initial result.
        # Never query the closed front Store on that result's return path.
        if self.front.phase=='WORKER_OWNED':
            require(caller is self.daemon and self.front.collectors,
                    'ROOT_ROUTER_WORKER_RESULT_WITHOUT_OWNED_COLLECTOR')
            return
        require(caller is self.daemon and self.front.phase=='FRONT_OWNED',
                'ROOT_ROUTER_PUBLICATION_OWNER_UNKNOWN')
        caller.publisher.publish()

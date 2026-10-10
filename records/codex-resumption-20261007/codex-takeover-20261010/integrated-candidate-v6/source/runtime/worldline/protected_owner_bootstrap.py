"""Explicit protected bootstrap composition seam; no import-time actuation.

Call only after the exact source lease has bound the actual Gate/Controller and
canonical recovery principal. Existing owner policy+journal+head and complete
resource ledger must already be owner-provisioned; absence never initializes.
The operator must source-qualify/prove the complete composition first.
"""
from pathlib import Path
from .protected_owner import ProtectedOwnerPrincipal,require
from .owner_intent_endpoint import OwnerIntentEndpoint,OwnerIntentServer

def attach_owner(startup_lease,principal):
    import recovery_principal
    import run_service
    from .protected_startup import StartupLease
    require(type(startup_lease) is StartupLease and type(principal) is recovery_principal.ProtectedRecoveryPrincipal,
        'OWNER_BOOTSTRAP_ACTUAL_TYPES_REQUIRED')
    startup_lease.intact()
    require(startup_lease.principal is principal and principal.gate is startup_lease.gate
        and principal.capture.controller is startup_lease.controller and principal.capture.startup_lease is startup_lease,
        'OWNER_BOOTSTRAP_EXCLUSIVE_LEASE_CHANGED')
    require(not hasattr(startup_lease.controller,'protected_owner'),'OWNER_BOOTSTRAP_ALREADY_ATTACHED')
    root=Path(startup_lease.spec['paths']['authority_root'])/'authority/resource'
    resources=run_service.RunLedgerService(root)
    owner=ProtectedOwnerPrincipal(principal.gate,startup_lease.controller,resources,startup_lease=startup_lease)
    # Bind this exact source endpoint before any external acceptance. No daemon
    # request chooses a principal, source, grant, epoch or protected observation.
    endpoint=OwnerIntentEndpoint(owner)
    return owner,OwnerIntentServer(endpoint)
